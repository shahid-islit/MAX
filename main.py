import sys
import os
sys.stderr = open(os.devnull, 'w')

import time
import keyboard
from rich.console import Console
from rich.panel import Panel
from brain import ask_max
from tts import speak
from voice import listen
from config import MAX_NAME, USER_NAME

console = Console()

def confirm_voice_input(transcript: str) -> bool:
    console.print(f"\n[bold yellow]⚠ MAX heard:[/bold yellow] {transcript}")
    console.print(f"[dim]Press ESC within 7 seconds to cancel...[/dim]")
    
    start = time.time()
    while time.time() - start < 7:
        if keyboard.is_pressed("esc"):
            console.print(f"[bold red]❌ Cancelled.[/bold red]")
            speak("Cancelled.")
            return False
        time.sleep(0.05)
    return True

def main():
    welcome = f"Welcome back, {USER_NAME}. I'm {MAX_NAME}, online and ready."
    console.print(Panel(f"[bold cyan]{welcome}[/bold cyan]\nSay or type [bold]'voice'[/bold] to switch to voice input. Say or type [bold]'exit'[/bold] to quit.", border_style="cyan"))
    speak(welcome)

    voice_mode = False

    while True:
        try:
            if voice_mode:
                console.print(f"\n[bold yellow]🎙️ Voice mode — press Enter to start, Enter again to stop.[/bold yellow]")
                user_input = listen()
                console.print(f"\n[bold green]{USER_NAME}:[/bold green] {user_input}")

                if not confirm_voice_input(user_input):
                    continue
            else:
                user_input = console.input(f"\n[bold green]{USER_NAME}:[/bold green] ")

            cleaned = user_input.strip().lower().rstrip(".,!?")

            if any(word in cleaned for word in ["exit", "quit", "bye"]):
                farewell = f"Later, {USER_NAME}."
                console.print(f"\n[bold cyan]{MAX_NAME}:[/bold cyan] {farewell}")
                speak(farewell)
                break

            if "voice" in cleaned and "text" not in cleaned:
                voice_mode = True
                console.print(f"\n[bold cyan]{MAX_NAME}:[/bold cyan] Voice mode activated.")
                speak("Voice mode activated.")
                continue

            if "text" in cleaned or "type" in cleaned:
                voice_mode = False
                console.print(f"\n[bold cyan]{MAX_NAME}:[/bold cyan] Switched back to text mode.")
                speak("Switched back to text mode.")
                continue

            if not user_input.strip():
                continue

            with console.status(f"[cyan]{MAX_NAME} is thinking...[/cyan]"):
                response = ask_max(user_input)

            console.print(f"\n[bold cyan]{MAX_NAME}:[/bold cyan] {response}")
            if voice_mode:
                speak(response)

        except KeyboardInterrupt:
            farewell = f"Later, {USER_NAME}."
            console.print(f"\n[bold cyan]{MAX_NAME}:[/bold cyan] {farewell}")
            speak(farewell)
            break

if __name__ == "__main__":
    main()