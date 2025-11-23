import json
import logging
from dotenv import load_dotenv
from typing import Annotated, List, Optional
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    llm,
    function_tool,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit import rtc

import os
import sys

logger = logging.getLogger("agent")

# load_dotenv(".env.local")

# def check_env_vars():
#     required_vars = [
#         "LIVEKIT_URL",
#         "LIVEKIT_API_KEY",
#         "LIVEKIT_API_SECRET",
#         "DEEPGRAM_API_KEY",
#         "GOOGLE_API_KEY",
#         "MURF_API_KEY",
#     ]
#     missing = [var for var in required_vars if not os.getenv(var)]
#     if missing:
#         logger.error(f"Missing required environment variables: {', '.join(missing)}")
#         logger.error("Please check your .env.local file.")
#         # We might want to exit or just let it fail, but logging is helpful.
#         # sys.exit(1) # Optional: force exit

# check_env_vars()



def save_order_to_file(order: dict):
    try:
        # Ensure directory exists
        os.makedirs("backend/src", exist_ok=True)
        with open("backend/src/orders.json", "a") as f:
            json.dump(order, f)
            f.write("\n")
    except Exception as e:
        logger.error(f"Failed to save order to file: {e}")
        raise


class Barista(Agent):
    def __init__(self, room: rtc.Room) -> None:
        super().__init__(
            instructions="""You are a friendly and efficient barista at 'CodeBrew Coffee'.
            Your goal is to take the customer's coffee order.
            
            You need to collect the following information to complete an order:
            1. Drink Type (e.g., Coffee, Latte, Cappuccino)
            2. Size (Small, Medium, Large)
            3. Milk preference (if applicable)
            4. Any extras (optional)
            5. Customer Name
            
            Ask clarifying questions one by one to fill in missing details. 
            Do not assume any details unless the user specifies them.
            
            Once you have all the details, confirm the full order with the customer.
            If they say yes, use the `submit_order` tool to finalize it.
            
            Be polite, energetic, and use coffee puns occasionally.
            """,
        )
        self.room = room
        self.order = {
            "drinkType": None,
            "size": None,
            "milk": None,
            "extras": [],
            "name": None,
        }

    @function_tool
    async def update_order(
        self,
        drink_type: Annotated[Optional[str], "Type of drink (e.g., Coffee, Latte, Cappuccino)"] = None,
        size: Annotated[Optional[str], "Size of the drink (Small, Medium, Large)"] = None,
        milk: Annotated[Optional[str], "Type of milk (Whole, Skim, Oat, Almond, Soy, None)"] = None,
        extras: Annotated[Optional[List[str]], "List of extras (e.g., Whipped Cream, Sugar, Syrup)"] = None,
        name: Annotated[Optional[str], "Customer's name"] = None,
    ):
        """Update the current order details."""
        if drink_type:
            self.order["drinkType"] = drink_type
        if size:
            self.order["size"] = size
        if milk:
            self.order["milk"] = milk
        if extras is not None:
            self.order["extras"] = extras
        if name:
            self.order["name"] = name
        
        logger.info(f"Order updated: {self.order}")
        # Publish partial order to frontend for real‑time preview
        try:
            await self.room.local_participant.publish_data(
                json.dumps(self.order).encode(),
                topic="order_update",
            )
        except Exception as e:
            logger.error(f"Failed to publish order update: {e}")
        return f"Current order state: {json.dumps(self.order)}"

    @function_tool
    async def submit_order(self):
        """Call this when the user confirms the order is correct and complete."""
        # Check if required fields are present (basic validation)
        required_fields = ["drinkType", "size", "name"]
        missing = [f for f in required_fields if not self.order.get(f)]
        
        if missing:
            return f"Cannot submit order. Missing details: {', '.join(missing)}. Please ask the user for these."

        # Save to file
        try:
            save_order_to_file(self.order)
            
            summary = f"Order submitted for {self.order['name']}: {self.order['size']} {self.order['drinkType']}"
            if self.order.get('milk'):
                summary += f" with {self.order['milk']}"
            if self.order.get('extras'):
                summary += f" and {', '.join(self.order['extras'])}"
            
            # Generate HTML Receipt
            receipt_html = f"""
            <div class="text-center">
                <h2 class="text-2xl font-bold mb-4 coffee-accent" style="border-bottom: 1px dashed var(--coffee-accent); padding-bottom: 10px;">CodeBrew Coffee</h2>
                <div class="space-y-2 text-left inline-block">
                    <p><strong class="coffee-accent">Customer:</strong> {self.order['name']}</p>
                    <p><strong class="coffee-accent">Item:</strong> {self.order['size']} {self.order['drinkType']}</p>
                    <p><strong class="coffee-accent">Milk:</strong> {self.order.get('milk', 'None')}</p>
                    <p><strong class="coffee-accent">Extras:</strong> {', '.join(self.order['extras']) if self.order['extras'] else 'None'}</p>
                </div>
                <div class="mt-6 pt-4 border-t border-dashed border-coffee-accent">
                    <p class="text-xl italic">Thank you!</p>
                </div>
            </div>
            """
            
            # Publish receipt to frontend
            logger.info("Publishing receipt data...")
            await self.room.local_participant.publish_data(
                receipt_html, 
                topic="receipt"
            )
            
            return f"Order saved successfully! Summary: {summary}"
        except Exception as e:
            logger.error(f"Failed to save order or publish receipt: {e}")
            return "Failed to save order due to an internal error."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(
            model="gemini-2.5-flash",
        ),
        tts=murf.TTS(
            voice="en-US-matthew", 
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Start the session with the Barista agent and tools
    await session.start(
        agent=Barista(room=ctx.room),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
