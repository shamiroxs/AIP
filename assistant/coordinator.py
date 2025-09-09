from assistant.agents.response import ResponseAgent
from assistant.agents.intent_recognition import IntentRecognitionAgent
from assistant.agents.action_execution import ActionExecutionAgent
from assistant.config.settings import settings
from assistant.utils.logger import get_logger

log = get_logger(__name__)

class Coordinator:
    def __init__(self):
        self.resp = ResponseAgent()
        self.intent = IntentRecognitionAgent()
        self.exec = ActionExecutionAgent(self._confirm)

    def handle_text(self, text: str):
        text = text.strip()
        log.info("[Heard] %s", text)
        # wake word gating
        if not text.lower().startswith(settings.WAKE_WORD + " "):
            return  # ignore non-wake phrases
        command = text[len(settings.WAKE_WORD)+1:].strip()
        if not command:
            self.resp.say("Yes?")
            return
        it = self.intent.parse(command)
        if not it:
            self.resp.say("I didn't understand that command yet.")
            return
        result = self.exec.run(it)
        self.resp.say(result if len(result) < 500 else "Done. I printed a long output to the console.")

    def _confirm(self, question: str) -> bool:
        # Minimal voice confirmation path: speak and wait for 'yes' in stdin fallback for now.
        # We’ll wire true voice confirmation later; for now we prompt via console.
        self.resp.say(question + " Say 'yes' to confirm.")
        try:
            print("[Type yes/no then Enter] ", end="", flush=True)
            ans = input().strip().lower()
            return ans in {"y", "yes"}
        except EOFError:
            return False
