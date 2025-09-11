# assistant/agents/confirm_agent.py
import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from assistant.config.settings import settings
from assistant.utils.logger import get_logger
from typing import Optional

log = get_logger(__name__)

class ConfirmAgent:
    """
    Short voice-based confirmation using Vosk.
    listen_confirm(timeout) -> True/False/None (None = no clear answer)
    """

    def __init__(self, model_dir: str | None = None, samplerate: int | None = None):
        model_dir = model_dir or settings.VOSK_MODEL_DIR
        samplerate = samplerate or settings.SAMPLE_RATE
        self._model = Model(model_dir)
        self._samplerate = samplerate
        self._q: queue.Queue[bytes] = queue.Queue()
        self._rec = KaldiRecognizer(self._model, self._samplerate)
        self._stream = None

    def _callback(self, indata, frames, time, status):
        if status:
            log.warning("[Confirm] %s", status)
        self._q.put(bytes(indata))

    def listen_confirm(self, timeout: float = 5.0) -> Optional[bool]:
        """
        Listen for `yes`/`no` for up to timeout seconds. Returns True/False or None.
        """
        log.info("[Confirm] Listening for %s seconds for yes/no...", timeout)
        recorded = bytearray()
        try:
            with sd.RawInputStream(samplerate=self._samplerate, blocksize=8000,
                                   dtype='int16', channels=1, callback=self._callback):
                import time as _time
                t0 = _time.time()
                while _time.time() - t0 < timeout:
                    try:
                        data = self._q.get(timeout=0.5)
                    except queue.Empty:
                        continue
                    recorded.extend(data)
                    if self._rec.AcceptWaveform(data):
                        res = json.loads(self._rec.Result())
                        txt = (res.get("text") or "").strip().lower()
                        if txt:
                            log.info("[Confirm] Heard (final): %s", txt)
                            if "yes" in txt or "yeah" in txt or "yup" in txt or "confirm" in txt:
                                return True
                            if "no" in txt or "nah" in txt or "cancel" in txt:
                                return False
                # Try partial
                partial = json.loads(self._rec.PartialResult()).get("partial", "")
                if partial:
                    p = partial.lower()
                    if "yes" in p: return True
                    if "no" in p: return False
        except Exception as e:
            log.warning("[Confirm] audio failure: %s", e)
        return None

    def ask_confirm(self, prompt_text: str, timeout: float = 6.0) -> bool:
        """
        Ask by voice then fallback to console. Returns True if confirmed.
        """
        # speak the prompt via ResponseAgent externally (Coordinator will call).
        # Here we only capture answer.
        val = self.listen_confirm(timeout=timeout)
        if val is not None:
            return val
        # Fallback to typed input
        print("[Confirm] Type yes/no then Enter: ", end="", flush=True)
        try:
            ans = input().strip().lower()
            return ans in ("y", "yes")
        except Exception:
            return False
