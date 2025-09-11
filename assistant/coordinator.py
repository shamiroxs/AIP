# assistant/coordinator.py
from assistant.agents.response import ResponseAgent
from assistant.agents.intent_recognition import IntentRecognitionAgent
from assistant.agents.action_execution import ActionExecutionAgent
from assistant.agents.confirm_agent import ConfirmAgent
from assistant.config.settings import settings
from assistant.utils.logger import get_logger

log = get_logger(__name__)

class Coordinator:
    def __init__(self):
        self.resp = ResponseAgent()
        self.intent = IntentRecognitionAgent()
        self.confirm = ConfirmAgent()
        self.exec = ActionExecutionAgent(self._confirm_voice)

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
        # Trim overly long outputs for TTS
        if isinstance(result, str) and len(result) > 500:
            # speak short confirmation and print details to console
            self.resp.say("Done. Output is long; see console for details.")
            print(result)
        else:
            self.resp.say(result if isinstance(result, str) else str(result))

    def _confirm_voice(self, question: str) -> bool:
        # Speak the question and then listen for yes/no using ConfirmAgent
        self.resp.say(question)
        val = self.confirm.ask_confirm(question, timeout=6.0)
        log.info("[Confirm result] %s", val)
        if val is None:
            # fallback to keyboard + console
            self.resp.say("I didn't hear a clear response. Please type yes or no.")
            try:
                print("[Type yes/no then Enter] ", end="", flush=True)
                ans = input().strip().lower()
                return ans in {"y", "yes"}
            except Exception:
                return False
        return val
