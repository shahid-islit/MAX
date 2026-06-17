from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from brain import ask_max
from tts import speak
from groq import Groq
from config import GROQ_API_KEY
import threading
import tempfile
import os

# ─── RATE LIMITER ─────────────────────────────────────────────────────────────

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "app://.", "file://"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# ─── GROQ WHISPER CLIENT ──────────────────────────────────────────────────────

groq_client = Groq(api_key=GROQ_API_KEY)

# ─── MODELS ───────────────────────────────────────────────────────────────────

class Message(BaseModel):
    text: str

    class Config:
        # Prevent extra fields being injected
        extra = "forbid"

# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "MAX is online"}


@app.post("/chat")
@limiter.limit("30/minute")
def chat(request: Request, message: Message):
    text = message.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty input.")
    if len(text) > 2000:
        raise HTTPException(status_code=400, detail="Input too long. Max 2000 characters.")
    response = ask_max(text)
    return {"response": response}


@app.post("/speak")
@limiter.limit("20/minute")
def speak_text(request: Request, message: Message):
    text = message.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty input.")
    if len(text) > 2000:
        raise HTTPException(status_code=400, detail="Input too long.")
    thread = threading.Thread(target=speak, args=(text,))
    thread.daemon = True
    thread.start()
    return {"status": "speaking"}


@app.post("/transcribe")
@limiter.limit("20/minute")
async def transcribe(request: Request, file: UploadFile = File(...)):
    # Validate file type
    allowed_types = ["audio/wav", "audio/webm", "audio/ogg", "audio/mp4", "audio/mpeg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Must be audio."
        )

    # Validate file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Audio file too large. Max 10MB.")

    # Write to temp file and transcribe
    suffix = ".webm" if "webm" in file.content_type else ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            transcript = groq_client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=f,
                language="en"
            )
        return {"text": transcript.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        os.unlink(tmp_path)