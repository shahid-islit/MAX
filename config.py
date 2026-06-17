import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY        = os.getenv("GROQ_API_KEY")
ELEVENLABS_API_KEY  = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
MODEL_NAME          = "llama-3.1-8b-instant"
MAX_NAME            = "MAX"
USER_NAME           = "Shahid"