from pydantic import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "Debian Voice Assistant"
    WAKE_WORD: str = "leo"          # Say "leo ..." before a command
    SAMPLE_RATE: int = 16000
    VOSK_MODEL_DIR: str = str(Path(__file__).resolve().parent.parent / "models" / "vosk" / "en-in")
    ENABLE_TTS: bool = True
    # safety: require explicit "yes" confirmation for privileged actions
    REQUIRE_CONFIRMATION_FOR_ROOT: bool = True

    # LLM related settings
    LLM_ENABLED: bool = True               # Set True to enable contacting a local LLM server
    LLM_PROVIDER: str = "ollama"            # "ollama" or "mock"
    LLM_HOST: str = "http://127.0.0.1:11434" # endpoint used if LLM_ENABLED is True
    LLM_MODEL_NAME: str = "llama3.2:3B-instruct-q4_K_M"   # model identifier (provider-specific)
    LLM_TIMEOUT_SECONDS: int = 120

    CONVERSATION_MEMORY_SIZE: int = 8
    SUGGESTION_CONFIDENCE_THRESHOLD: float = 0.70


    HOME_DIR: str = str(Path.home())
    LEO_HOME: str = str(Path.home() / ".leo")
    LLM_LOG_FILE: str = str(Path.home() / ".leo" / "llm.log")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
