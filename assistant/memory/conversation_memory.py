# assistant/memory/conversation_memory.py

from assistant.memory.memory_store import MemoryStore


class ConversationMemory:
    def __init__(self):
        self.store = MemoryStore()

    def add(self, role: str, message: str):
        self.store.execute(
            "INSERT INTO conversations (role, message) VALUES (?, ?)",
            (role, message)
        )

    def recent(self, limit=10):
        rows = self.store.fetchall(
            "SELECT role, message FROM conversations ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return [
            {"role": row["role"], "content": row["message"]}
            for row in reversed(rows)
        ]

