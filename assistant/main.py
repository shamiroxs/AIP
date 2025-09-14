import argparse
from assistant.coordinator import Coordinator
from assistant.agents.voice_input import VoiceInputAgent

import os, zipfile, urllib.request, pathlib

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

    c = Coordinator()
    if args.text:
        c.handle_text(args.text)
        return

    # Continuous voice mode
    v = VoiceInputAgent()
    v.listen(c.handle_text)

if __name__ == "__main__":
    ensure_vosk_model()
    main()
