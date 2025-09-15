import json, queue, sys
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from assistant.config.settings import settings
from assistant.utils.logger import get_logger

log = get_logger(__name__)

command_list = [c.lower() for c in [
    "leo",
    "leo say",
    "leo open", 
    "leo install", 
    "leo shutdown", 
    "leo restart"
]]

class VoiceInputAgent:
    def __init__(self, model_dir: str | None = None, samplerate: int | None = None):
        model_dir = model_dir or settings.VOSK_MODEL_DIR
        samplerate = samplerate or settings.SAMPLE_RATE
        self.model = Model(model_dir)
        self.rec = KaldiRecognizer(self.model, samplerate, json.dumps(command_list))
        self.samplerate = samplerate
        self.q = queue.Queue()

    def _callback(self, indata, frames, time, status):
        if status:
            log.warning(str(status))
        self.q.put(bytes(indata))

    def listen(self, on_final_text):
        """Continuous listen; calls on_final_text(text) for each final phrase."""
        log.info("[Voice] Listening… say: '%s <command>'", settings.WAKE_WORD)
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, dtype='int16',
                               channels=1, callback=self._callback):
            while True:
                data = self.q.get()
                if self.rec.AcceptWaveform(data):
                    result = json.loads(self.rec.Result())
                    text = (result.get("text") or "").strip()
                    if text:
                        on_final_text(text)
                else:
                    # partial = json.loads(self.rec.PartialResult()).get("partial", "")
                    pass