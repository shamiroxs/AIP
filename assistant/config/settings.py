from pydantic import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "Debian Voice Assistant"
    WAKE_WORD: str = "assistant"          # Say "assistant ..." before a command
    SAMPLE_RATE: int = 16000
    VOSK_MODEL_DIR: str = str(Path(__file__).resolve().parent.parent / "models" / "vosk" / "en-us")
    ENABLE_TTS: bool = True
    # safety: require explicit "yes" confirmation for privileged actions
    REQUIRE_CONFIRMATION_FOR_ROOT: bool = True

settings = Settings()
