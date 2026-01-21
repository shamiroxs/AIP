import argparse
import threading
import sys
from assistant.coordinator import Coordinator
from assistant.agents.voice_input import VoiceInputAgent

from assistant.memory.conversation_memory import ConversationMemory
from assistant.memory.task_memory import TaskMemory
import os, zipfile, urllib.request, pathlib

def terminal_input_loop(handler):
    """
    Continuously read text from terminal and send to handler
    """
    print("💬 Terminal input enabled. Type your command and press Enter.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            text = input("> ").strip()
            if not text:
                continue
            if text.lower() in ("exit", "quit"):
                print("Exiting...")
                os._exit(0)  # hard exit to stop mic threads cleanly
            handler(text)
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting...")
            os._exit(0)


def ensure_vosk_model():
    model_dir = pathlib.Path("assistant/models/vosk/en-in")
    if model_dir.exists():
        return

    print("Vosk model not found, downloading...")
    model_dir.parent.mkdir(parents=True, exist_ok=True)

    url = "https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip"
    zip_path = model_dir.parent / "vosk-model-en-in-0.5.zip"

    urllib.request.urlretrieve(url, zip_path)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(model_dir.parent)

    os.rename(model_dir.parent / "vosk-model-en-in-0.5", model_dir)
    os.remove(zip_path)
    print(f"Model installed at {model_dir}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", help="Run a single text command (no mic). Example: --text 'assistant check disk'")
    args = ap.parse_args()

    conversation_memory = ConversationMemory()
    task_memory = TaskMemory()

    c = Coordinator()
    def handle_text_with_memory(user_text: str):
        # Store user input
        conversation_memory.add("user", user_text)

        # Resume / continue handling
        if user_text.lower() in ("continue", "resume", "go on"):
            task = task_memory.current_task()
            if task:
                c.resume_task(task)
            else:
                print("No active task to continue.")
            return

        # Normal flow
        response = c.handle_text(user_text)

        # Store assistant response (if any)
        if response:
            conversation_memory.add("assistant", response)

    if args.text:
        handle_text_with_memory(args.text)
        return

    # Start terminal input thread
    terminal_thread = threading.Thread(
        target=terminal_input_loop,
        args=(handle_text_with_memory,),
        daemon=True
    )
    terminal_thread.start()

    # Continuous voice mode
    v = VoiceInputAgent()
    v.listen(handle_text_with_memory)


if __name__ == "__main__":
    ensure_vosk_model()
    main()