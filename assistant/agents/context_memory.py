# assistant/agents/context_memory.py
import json
from collections import deque
from assistant.config.settings import settings
from assistant.utils.logger import get_logger
import os
from pathlib import Path

log = get_logger(__name__)

class ContextMemory:
    def __init__(self, size: int | None = None):
        self.size = size or settings.CONVERSATION_MEMORY_SIZE
        self.queue = deque(maxlen=self.size)
        self.persist_file = Path(settings.LEO_HOME) / "memory.json"
        # Try load existing memory
        try:
            if self.persist_file.exists():
                with open(self.persist_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for e in data[-self.size:]:
                        self.queue.append(e)
        except Exception as e:
            log.info("[Memory] no previous memory loaded: %s", e)

    def add_turn(self, user_input: str, reply: str, proposed: dict | None = None):
        entry = {"user": user_input, "reply": reply, "proposed": proposed}
        self.queue.append(entry)
        # persist small snapshot
        try:
            with open(self.persist_file, "w", encoding="utf-8") as f:
                json.dump(list(self.queue), f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.info("[Memory] persist failed: %s", e)

    def get_context_for_query(self) -> str:
        # Build a short context string summarizing last turns
        parts = []
        for e in list(self.queue):
            parts.append(f"USER: {e.get('user')}\nASSISTANT: {e.get('reply')}")
        return "\n\n".join(parts)
