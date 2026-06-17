from elevenlabs.client import ElevenLabs
from config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID
import pygame
import tempfile
import os
import time
import threading

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Init mixer once at module load
pygame.mixer.init()

_tts_lock = threading.Lock()

def speak(text: str):
    # Stop anything currently playing before starting new speech
    pygame.mixer.music.stop()

    text = text.replace("Shahid", "Sha-heed")

    audio = client.text_to_speech.convert(
        voice_id=ELEVENLABS_VOICE_ID,
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings={
            "stability": 0.28,
            "similarity_boost": 0.85,
            "style": 0.75,
            "speed": 0.85
        }
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        for chunk in audio:
            f.write(chunk)
        temp_path = f.name

    with _tts_lock:
        try:
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        finally:
            pygame.mixer.music.unload()
            for _ in range(5):
                try:
                    os.unlink(temp_path)
                    break
                except PermissionError:
                    time.sleep(0.1)

if __name__ == "__main__":
    speak("Hey Shahid, MAX is online.")