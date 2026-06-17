import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile
import os
from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

SAMPLE_RATE = 16000

def listen() -> str:
    print("🎙️ Listening... (press Enter when done speaking)")
    input()  # wait for user to press Enter to start
    
    print("🔴 Recording... (press Enter to stop)")
    recording = []
    
    def callback(indata, frames, time, status):
        recording.append(indata.copy())
    
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback):
        input()  # stop on Enter
    
    import numpy as np
    audio_data = np.concatenate(recording, axis=0)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        wav.write(f.name, SAMPLE_RATE, audio_data)
        temp_path = f.name
    
    with open(temp_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
             model="whisper-large-v3-turbo",
             file=f,
             language="en"
        )
    
    os.unlink(temp_path)
    return transcript.text

if __name__ == "__main__":
    print("Test voice input")
    result = listen()
    print(f"You said: {result}")