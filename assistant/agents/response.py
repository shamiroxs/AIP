import pyttsx3
from assistant.config.settings import settings
from assistant.utils.logger import get_logger

log = get_logger(__name__)

class ResponseAgent:
    def __init__(self):
        self.enabled = settings.ENABLE_TTS
        self.tts = None
        if self.enabled:
            self.tts = pyttsx3.init()

    def say(self, text: str):
        log.info("[Say] %s", text)
        if self.enabled and self.tts:
            self.tts.say(text)
            self.tts.runAndWait()
        return text
