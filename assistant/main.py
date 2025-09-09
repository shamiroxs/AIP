import argparse
from assistant.coordinator import Coordinator
from assistant.agents.voice_input import VoiceInputAgent

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
    main()
