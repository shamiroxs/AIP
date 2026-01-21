# assistant/memory/user_preferences.py

from assistant.memory.memory_store import MemoryStore


class UserPreferences:
    def __init__(self):
        self.store = MemoryStore()

    def set(self, key: str, value: str):
        self.store.execute(
            "INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)",
            (key, value)
        )

    def get(self, key: str, default=None):
        rows = self.store.fetchall(
            "SELECT value FROM preferences WHERE key = ?",
            (key,)
        )
        return rows[0]["value"] if rows else default
