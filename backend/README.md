# Backend - Teach-the-Tutor AI Agent

Python-based LiveKit agent with 3 learning modes and dynamic voice switching.

## Quick Start

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env.local
# Edit .env.local with your API keys

# Download models
uv run python src/agent.py download-files

# Run agent
uv run python src/agent.py dev
```

## Environment Variables

Required in `.env.local`:

```bash
LIVEKIT_URL=ws://127.0.0.1:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
MURF_API_KEY=your_murf_api_key
GOOGLE_API_KEY=your_google_api_key
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
```

## Project Structure

```
backend/
├── shared-data/
│   └── day4_tutor_content.json    # Programming concepts
├── src/
│   ├── agent.py                    # Main agent with 3 modes
│   └── __init__.py
├── .env.example                    # Environment template
└── pyproject.toml                  # Dependencies
```

## Features

- **3 Learning Modes**: Learn, Quiz, Teach-Back
- **Dynamic Voice Switching**: Matthew, Alicia, Ken (Murf Falcon)
- **Real-time STT**: AssemblyAI speech recognition
- **LLM**: Google Gemini 2.5 Flash
- **Framework**: LiveKit Agents

## API Keys

Get free API keys from:
- **Murf Falcon**: https://murf.ai/api
- **Google Gemini**: https://ai.google.dev/
- **AssemblyAI**: https://www.assemblyai.com/

## Documentation

See the [main README](../README.md) for complete setup instructions.

## Tech Stack

- Python 3.12
- LiveKit Agents 1.3.2
- Murf Falcon TTS
- AssemblyAI STT
- Google Gemini LLM
- Silero VAD

---

Part of the **Murf AI Voice Agents Challenge - Day 4**
