import json
import logging
import os
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import Field, AliasChoices

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    tokenize,
    llm,
    function_tool,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit import rtc

# ---------------------------------------------------------------------------
# Logging & environment
# ---------------------------------------------------------------------------
logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(ch)

load_dotenv(".env.local")

# ---------------------------------------------------------------------------
# Barista Agent
# ---------------------------------------------------------------------------
class Barista(Agent):
    """Voice-driven barista that takes coffee orders."""

    def __init__(self, room: rtc.Room) -> None:
        # Pass instructions to the Agent base class (optional)
        instructions = (
            "You are a friendly and efficient barista at 'coffeebucks'.\n\n"
            "IMPORTANT: You must call the `update_order` tool IMMEDIATELY whenever the user provides "
            "any new information (drink, size, milk, etc.), even if the order is incomplete. "
            "Do not wait to collect all fields. Update the screen first, then ask the next question.\n\n"
            "Collect the following information one-by-one:\n"
            "1. Drink Type (Coffee, Latte, Cappuccino, ...)\n"
            "2. Size (Small, Medium, Large)\n"
            "3. Milk preference (Whole, Skim, Oat, Almond, Soy, None)\n"
            "4. Extras (optional list like Syrup, Caramel, Whipped Cream)\n"
            "5. Customer name\n\n"
            "Ask clarifying questions when a field is missing. Confirm final order and "
            "call submit_order when the customer confirms."
        )
        super().__init__(instructions=instructions)
        self.room = room

        # canonical order state
        self.order: dict = {
            "drinkType": None,
            "size": None,
            "milk": None,
            "extras": [],
            "name": None,
        }

# ---------------------------------------------------------------------------
# Tools — NOTE: these are plain functions exposed as tools to the LLM.
# They MUST NOT include 'self' in the signature.
# Use llm.current_agent to access the Barista instance (agent state).
# ---------------------------------------------------------------------------

@function_tool
async def update_order(
    drink_type: Optional[str] = None,
    size: Optional[str] = None,
    milk: Optional[str] = None,
    extras: Optional[List[str]] = None,
    name: Optional[
        str
    ] = Field(
        default=None,
        # Accept these alias names from the model: "name", "customer", "customerName", "customer_name"
        validation_alias=AliasChoices("name", "customer", "customerName", "customer_name"),
    ),
) -> dict:
    """
    Update the current order. Only provided fields are applied.
    Returns the new order state as {'order': {...}}.
    """

    # Retrieve the active agent instance and its state
    agent = llm.current_agent
    if agent is None:
        logger.error("No current agent available in update_order")
        return {"status": "error", "message": "no agent instance"}

    # type: ignore helps type checkers; at runtime this is the Barista instance
    barista: Barista = agent  # type: ignore

    # Apply partial updates only for provided args
    if drink_type is not None:
        barista.order["drinkType"] = drink_type

    if size is not None:
        barista.order["size"] = size

    if milk is not None:
        barista.order["milk"] = milk

    if extras is not None:
        # ensure extras is a list
        barista.order["extras"] = extras

    if name is not None:
        barista.order["name"] = name

    logger.info(f"Order updated: {barista.order}")
    
    # Publish partial update to frontend
    try:
        payload = {**barista.order, "status": "in_progress"}
        await barista.room.local_participant.publish_data(json.dumps(payload), topic="receipt")
    except Exception:
        logger.exception("Failed to publish update")

    return {"status": "ok", "order": barista.order}


@function_tool
async def submit_order() -> dict:
    """
    Validate the current order, persist it to order.json, publish an HTML receipt,
    and return a summary dict.
    """

    agent = llm.current_agent
    if agent is None:
        logger.error("No current agent available in submit_order")
        return {"status": "error", "message": "no agent instance"}

    barista: Barista = agent  # type: ignore

    required_fields = ["drinkType", "size", "milk", "extras", "name"]
    missing = [f for f in required_fields if not barista.order.get(f)]
    if missing:
        logger.info(f"submit_order: missing fields {missing}")
        return {"status": "error", "message": f"Missing fields: {', '.join(missing)}"}

    # Persist order
    try:
        with open("orders.json", "w", encoding="utf-8") as f:
            json.dump(barista.order, f, indent=2)
        logger.info("orders.json written successfully.")
    except Exception as e:
        logger.exception("Failed to write orders.json")
        return {"status": "error", "message": "Failed to write orders.json"}

    # Build a readable summary
    extras_str = ", ".join(barista.order["extras"]) if barista.order["extras"] else "None"
    summary = (
        f"Order for {barista.order['name']}: {barista.order['size']} "
        f"{barista.order['drinkType']} with {barista.order['milk']}. Extras: {extras_str}"
    )

    # Publish receipt to the frontend via LiveKit data channel (non-blocking best-effort)
    try:
        logger.info("Publishing receipt to LiveKit data channel...")
        receipt_data = json.dumps({**barista.order, "status": "completed"})
        await barista.room.local_participant.publish_data(receipt_data, topic="receipt")
        logger.info("Receipt published.")
    except Exception as e:
        logger.exception("Failed to publish receipt (continuing)")

    return {"status": "success", "summary": summary, "order": barista.order}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def prewarm(proc: JobProcess) -> None:
    """Pre-warm heavy models to reduce first-request latency."""
    proc.userdata["vad"] = silero.VAD.load()


# ---------------------------------------------------------------------------
# Entrypoint for the LiveKit worker
# ---------------------------------------------------------------------------
async def entrypoint(ctx: JobContext) -> None:
    ctx.log_context_fields = {"room": ctx.room.name}

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Start the session with an instance of Barista (agent state lives on the instance)
    await session.start(
        agent=Barista(room=ctx.room),
        room=ctx.room,
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
    )

    await ctx.connect()


# ---------------------------------------------------------------------------
# Run as a standalone script (useful for local debugging)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
