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
        lines = text.strip().splitlines()
        for line in lines:
            log.info("[Say] %s", line)
            if self.enabled and self.tts:
                self.tts.say(line)
                self.tts.runAndWait()
        return text
