import subprocess
import tempfile
from pathlib import Path

from assistant.config.settings import settings
from assistant.utils.logger import get_logger

log = get_logger(__name__)

'''
    Configuration:
        sudo rm /usr/bin/piper
        sudo ln -s "$(pwd)/piper/piper" /usr/bin/piper
        ls -l /usr/bin/piper
        piper --help

'''
PIPER_DIR = Path.home() / ".local/share/piper/voices"
PIPER_MODEL = PIPER_DIR / "en_US-amy-medium.onnx"
PIPER_CONFIG = PIPER_DIR / "en_US-amy-medium.onnx.json"

class ResponseAgent:
    def __init__(self):
        self.enabled = settings.ENABLE_TTS

        if self.enabled:
            if not PIPER_MODEL.exists():
                raise RuntimeError(f"Missing Piper model: {PIPER_MODEL}")
            if not PIPER_CONFIG.exists():
                raise RuntimeError(f"Missing Piper config: {PIPER_CONFIG}")

    def say(self, text: str):
        if not self.enabled:
            return text

        if not isinstance(text, str):
            text = str(text)

        for line in text.strip().splitlines():
            log.info("[Say] %s", line)
            self._speak(line)

        return text

    def _speak(self, text: str):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as wav:
            subprocess.run(
                [
                    "piper",
                    "--model", str(PIPER_MODEL),
                    "--config", str(PIPER_CONFIG),
                    "--length_scale", "1",
                    "--noise_scale", "0.667",
                    "--sentence_silence", "0.2",
                    "--output_file", wav.name,
                    "--quiet",
                ],
                input=text.encode("utf-8"),
                stdout=subprocess.DEVNULL,   # <- silence stdout
                stderr=subprocess.DEVNULL,   # <- silence stderr
                check=True
            )

            subprocess.run(
                ["aplay", wav.name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
