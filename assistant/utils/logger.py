# assistant/utils/logger.py
import logging
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
from assistant.config.settings import settings
from pathlib import Path
import os

def _ensure_log_path():
    p = Path(settings.LEO_HOME)
    p.mkdir(parents=True, exist_ok=True)

    log_file = Path(settings.LLM_LOG_FILE).expanduser()
    log_file.parent.mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    _ensure_log_path()
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Console handler (rich)
    ch = RichHandler(rich_tracebacks=True)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))

    # LLM/audit file handler
    fh = RotatingFileHandler(settings.LLM_LOG_FILE, maxBytes=2_000_000, backupCount=3)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger
