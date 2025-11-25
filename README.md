# 🎓 AI Tutor: AI Active Recall Coach

An AI-powered voice tutoring system that helps users master programming concepts through active recall. Features three distinct learning modes with different Murf Falcon voices for an immersive educational experience.

**Built for the Murf AI Voice Agents Challenge - Day 4**

## ✨ Features

### Three Learning Modes

1. **📚 Learn Mode** (Matthew voice)
   - AI explains programming concepts clearly and patiently
   - Uses simple language and real-world examples
   - Interactive Q&A after explanations

2. **❓ Quiz Mode** (Alicia voice)
   - Tests knowledge with targeted questions
   - Provides constructive feedback
   - Adapts to user responses

3. **🎯 Teach-Back Mode** (Ken voice)
   - User explains concepts back to the AI
   - Receives detailed constructive feedback
   - Identifies knowledge gaps

### Key Features
- **Dynamic Voice Switching**: Three distinct Murf Falcon voices (Matthew, Alicia, Ken)
- **Seamless Mode Transitions**: Switch between modes anytime during conversation
- **5 Programming Concepts**: Variables, Loops, Functions, Conditionals, Data Types
- **Real-time Voice Interaction**: Natural conversation flow
- **Professional UI**: Smooth animations and modern design

## 🛠️ Tech Stack

- **TTS**: Murf Falcon (fastest text-to-speech API)
- **STT**: AssemblyAI (high-accuracy speech recognition)
- **LLM**: Google Gemini 2.5 Flash
- **Framework**: LiveKit Agents
- **Frontend**: Next.js 15 + React 19
- **Backend**: Python 3.12
- **Styling**: Tailwind CSS

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ with [uv](https://docs.astral.sh/uv/) package manager
- Node.js 18+ with pnpm
- [LiveKit Server](https://github.com/livekit/livekit/releases)

### 1. Clone Repository

```bash
git clone https://github.com/Gangadhar-NG-CODER/AI Tutor-ai-voice-agent.git
cd AI Tutor-ai-voice-agent
```

### 2. Get API Keys

You'll need free API keys from:
- **Murf Falcon**: https://murf.ai/api
- **Google Gemini**: https://ai.google.dev/
- **AssemblyAI**: https://www.assemblyai.com/

### 3. Backend Setup

```bash
cd backend

# Install dependencies
uv sync

# Copy and configure environment
cp .env.example .env.local

# Edit .env.local with your API keys:
# LIVEKIT_URL=ws://127.0.0.1:7880
# LIVEKIT_API_KEY=devkey
# LIVEKIT_API_SECRET=secret
# MURF_API_KEY=your_murf_api_key
# GOOGLE_API_KEY=your_google_api_key
# ASSEMBLYAI_API_KEY=your_assemblyai_api_key

# Download required models
uv run python src/agent.py download-files
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Copy and configure environment
cp .env.example .env.local

# Edit .env.local:
# LIVEKIT_API_KEY=devkey
# LIVEKIT_API_SECRET=secret
# LIVEKIT_URL=ws://127.0.0.1:7880
```

### 5. Run the Application

**Terminal 1 - LiveKit Server:**
```bash
# Download from: https://github.com/livekit/livekit/releases
livekit-server --dev
```

**Terminal 2 - Backend:**
```bash
cd backend
uv run python src/agent.py dev
```

**Terminal 3 - Frontend:**
```bash
cd frontend
pnpm dev
```

Open **http://localhost:3000** in your browser! 🎉

## 💡 How to Use

1. Click "Start Learning" on the welcome screen
2. The coordinator will greet you and explain the three modes
3. Choose your preferred mode:
   - Say "I want to learn about variables" for Learn mode
   - Say "Quiz me on loops" for Quiz mode
   - Say "I'll teach you about functions" for Teach-Back mode
4. Switch modes anytime by saying "Switch to [mode] mode"

## 📁 Project Structure

```
AI Tutor-ai-voice-agent/
├── backend/
│   ├── shared-data/
│   │   └── day4_tutor_content.json    # Programming concepts database
│   ├── src/
│   │   ├── agent.py                    # Main agent with 3 modes
│   │   └── __init__.py
│   ├── .env.example
│   ├── pyproject.toml
│   └── README.md
├── frontend/
│   ├── app/
│   ├── components/
│   ├── styles/
│   ├── .env.example
│   ├── package.json
│   └── README.md
├── DEMO_SCRIPT.md                      # Video recording guide
├── LINKEDIN_POST.md                    # Social media template
├── .gitignore
└── README.md
```

## 🎬 Demo

Check out `DEMO_SCRIPT.md` for a complete guide on recording your demo video.

## � *Available Concepts

- **Variables**: Data storage and reuse
- **Loops**: Iteration and repetition
- **Functions**: Code organization and reusability
- **Conditionals**: Decision making in code
- **Data Types**: Different kinds of values

## 🔧 Technical Implementation

### Voice Switching
Uses `agent_session.tts.update_options()` to dynamically change Murf Falcon voices:
- Matthew (en-US-matthew) for Learn mode
- Alicia (en-US-alicia) for Quiz mode
- Ken (en-US-ken) for Teach-Back mode

### Mode Management
Three function tools handle mode switching:
- `switch_to_learn_mode()`
- `switch_to_quiz_mode()`
- `switch_to_teach_back_mode()`

Each tool updates the voice and provides mode-specific instructions.

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built for the **Murf AI Voice Agents Challenge**
- Powered by **Murf Falcon TTS** - The fastest text-to-speech API
- Based on [LiveKit Agents](https://docs.livekit.io/agents)

## 🔗 Links

- [Murf Falcon Documentation](https://murf.ai/api/docs/text-to-speech/streaming)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents)
- [AssemblyAI Documentation](https://www.assemblyai.com/docs)

## 📱 Social Media

Part of the **#MurfAIVoiceAgentsChallenge** • **#10DaysofAIVoiceAgents**

---

**Built with ❤️ for the Murf AI Voice Agents Challenge**
