# MAX — Personal AI Assistant

A Jarvis-style personal AI assistant with voice input, voice output, and PC automation. Built with a multi-process architecture: Electron HUD frontend, Express middleware, FastAPI backend, and SQLite memory.

![MAX HUD](https://i.imgur.com/placeholder.png)

---

## Features

- 🎙 **Voice input** — speak to MAX via Groq Whisper (whisper-large-v3-turbo)
- 🔊 **Voice output** — MAX speaks back via ElevenLabs TTS
- 🧠 **Persistent memory** — remembers facts across sessions via SQLite
- 🖥 **PC automation** — open apps, websites, folders, and files by voice
- ⚡ **Action routing** — classifies intent and routes to the right action automatically
- 🌐 **Electron HUD** — gold particle orb interface built with Three.js + GSAP
- 🔒 **Rate limited API** — FastAPI backend with input validation and rate limiting

---

## Architecture

```
MAX/
├── electron/          # Electron + Three.js + GSAP frontend (HUD)
├── server/            # Express.js WebSocket middleware (port 3000)
├── api.py             # FastAPI backend (port 8000)
├── brain.py           # Groq LLM — action routing + conversation
├── memory.py          # SQLite persistent memory
├── tts.py             # ElevenLabs text-to-speech
├── voice.py           # Groq Whisper speech-to-text
├── actions.py         # PC automation (apps, websites, folders)
└── app_scanner.py     # Installed app scanner
```

**Startup flow:**
1. FastAPI backend starts on port 8000
2. Express + WebSocket server starts on port 3000
3. Electron HUD connects to WebSocket and loads the interface
4. Voice input → `/transcribe` (Whisper) → `/chat` (brain) → `/speak` (ElevenLabs)

---

## Requirements

- Python 3.12+
- Node.js 18+
- A microphone and speakers

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/shahid-islit/MAX.git
cd MAX
```

### 2. Create your `.env` file
```bash
cp .env.example .env
```
Fill in your API keys in `.env`.

### 3. Python backend
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
```

### 4. Express server
```bash
cd server
npm install
cd ..
```

### 5. Electron frontend
```bash
cd electron
npm install
cd ..
```

---

## API Keys Required

| Key | Where to get it | Used for |
|-----|----------------|---------|
| `GROQ_API_KEY` | https://console.groq.com/keys | LLM brain + Whisper transcription |
| `ELEVENLABS_API_KEY` | https://elevenlabs.io/app/settings/api-keys | Voice output (TTS) |
| `ELEVENLABS_VOICE_ID` | ElevenLabs voice library | Which voice MAX uses |

Create a `.env` file in the MAX root (see `.env.example`).

---

## Running MAX

Open 3 terminals:

**Terminal 1 — FastAPI backend:**
```bash
source venv/Scripts/activate
uvicorn api:app --port 8000
```

**Terminal 2 — Express server:**
```bash
cd server
node index.js
```

**Terminal 3 — Electron HUD:**
```bash
cd electron
npm start
```

---

## Usage

- **Type** a message in the input bar and press Enter or ▶
- **Click 🎙** to record voice — click again or wait 7 seconds to send
- **Press ESC** during recording to cancel
- Say **"open [app name]"** to launch apps
- Say **"open [website]"** to open websites in Chrome
- Say **"open my [folder name] folder"** to open registered folders

---

## Security Notes

- Never commit your `.env` file — it's in `.gitignore`
- `app_cache.json` and `max_memory.db` are generated locally and gitignored
- All FastAPI endpoints are rate limited
- CORS is restricted to localhost origins only

---

## Built With

- [Groq](https://groq.com) — LLM inference + Whisper transcription
- [ElevenLabs](https://elevenlabs.io) — Text to speech
- [FastAPI](https://fastapi.tiangolo.com) — Python backend
- [Electron](https://electronjs.org) — Desktop app shell
- [Three.js](https://threejs.org) — 3D particle orb
- [GSAP](https://greensock.com/gsap/) — Animations
- [SQLite](https://sqlite.org) — Persistent memory

---

## License

MIT — see [LICENSE](LICENSE)
