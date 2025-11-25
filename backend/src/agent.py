import logging
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from dotenv import load_dotenv
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
    function_tool,
    RunContext,
)
from livekit.plugins import murf, silero, google, noise_cancellation, assemblyai
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Load concepts
content_path = Path(__file__).parent.parent / "shared-data" / "day4_tutor_content.json"
with open(content_path, "r") as f:
    CONCEPTS = json.load(f)

concept_list = "\n".join([
    f"- {c['title']} (ID: {c['id']}): {c['summary']}"
    for c in CONCEPTS
])


@dataclass
class Userdata:
    agent_session: Optional[AgentSession] = None
    current_mode: str = "coordinator"


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


class TutorAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=f"""You are Mathew - an AI tutor that helps users master programming concepts.

You have THREE learning modes:

1. **LEARN mode** - You explain programming concepts clearly and patiently (Voice: Matthew)
2. **QUIZ mode** - You ask questions to test the user's knowledge (Voice: Alicia)
3. **TEACH-BACK mode** - The user explains concepts back to you, and you provide constructive feedback (Voice: Ken)

Available programming concepts:
{concept_list}

**Your behavior:**

INITIAL GREETING:
- Warmly greet the user
- Briefly explain the three modes
- Ask which mode they'd like to start with

WHEN IN LEARN MODE:
- Explain concepts using the summaries provided above
- Use simple language and real-world examples
- Be encouraging and patient
- After explaining, ask if they have questions or want to learn another concept

WHEN IN QUIZ MODE:
- Ask questions about the concepts (use sample questions as guides)
- Listen to their answers carefully
- Provide constructive feedback - praise correct answers, give hints for struggles
- Keep questions clear and focused on understanding

WHEN IN TEACH-BACK MODE:
- Ask the user to explain a concept in their own words
- Listen carefully to their explanation
- Compare it to the correct summary above
- Provide specific, constructive feedback:
  * Point out what they got right
  * Gently correct any misconceptions
  * Highlight important points they might have missed
- Be encouraging - learning is a process!

MODE SWITCHING:
- Users can switch modes anytime by asking
- When they request a mode switch, use the appropriate tool to switch
- The voice will change automatically for each mode

Keep your responses conversational and natural. You're speaking, not writing, so avoid complex formatting.""",
        )

    @function_tool
    async def switch_to_learn_mode(self, context: RunContext[Userdata]):
        """Use this tool when the user wants to enter LEARN mode to have concepts explained to them.
        
        Call this when they say things like:
        - "I want to learn about X"
        - "Teach me about X"
        - "Explain X to me"
        - "Switch to learn mode"
        """
        logger.info("Switching to Learn mode with Matthew voice")
        
        # Update voice to Matthew
        agent_session = context.userdata.agent_session
        if agent_session:
            agent_session.tts.update_options(voice="en-US-matthew", style="Conversation")
        
        context.userdata.current_mode = "learn"
        
        return "Great! I'm Matthew, and I'll be your teacher in Learn mode. I'll explain concepts clearly and patiently. Which concept would you like to learn about? We have Variables, Loops, Functions, Conditionals, and Data Types."

    @function_tool
    async def switch_to_quiz_mode(self, context: RunContext[Userdata]):
        """Use this tool when the user wants to enter QUIZ mode to be tested on their knowledge.
        
        Call this when they say things like:
        - "Quiz me on X"
        - "Test my knowledge"
        - "Ask me questions"
        - "Switch to quiz mode"
        """
        logger.info("Switching to Quiz mode with Alicia voice")
        
        # Update voice to Alicia
        agent_session = context.userdata.agent_session
        if agent_session:
            agent_session.tts.update_options(voice="en-US-alicia", style="Conversation")
        
        context.userdata.current_mode = "quiz"
        
        return "Excellent! I'm Alicia, and I'll be quizzing you to test your knowledge. Which concept should I test you on? I can quiz you on Variables, Loops, Functions, Conditionals, or Data Types."

    @function_tool
    async def switch_to_teach_back_mode(self, context: RunContext[Userdata]):
        """Use this tool when the user wants to enter TEACH-BACK mode to explain concepts back.
        
        Call this when they say things like:
        - "I want to explain X"
        - "Let me teach you about X"
        - "I'll explain X back to you"
        - "Switch to teach-back mode"
        """
        logger.info("Switching to Teach-Back mode with Ken voice")
        
        # Update voice to Ken
        agent_session = context.userdata.agent_session
        if agent_session:
            agent_session.tts.update_options(voice="en-US-ken", style="Conversation")
        
        context.userdata.current_mode = "teach_back"
        
        return "Perfect! I'm Ken, and I'll listen carefully to your explanations and provide constructive feedback. Which concept would you like to teach me about? You can explain Variables, Loops, Functions, Conditionals, or Data Types."


async def entrypoint(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room,
    }

    # Initialize userdata
    userdata = Userdata()

    # Create session with Matthew voice (default)
    session = AgentSession(
        stt=assemblyai.STT(),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
        userdata=userdata,
    )

    # Store session in userdata for tools to access
    userdata.agent_session = session

    # Metrics collection
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start session
    await session.start(
        agent=TutorAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
