# assistant/memory/task_memory.py

from assistant.memory.memory_store import MemoryStore


class TaskMemory:
    def __init__(self):
        self.store = MemoryStore()

    def start_task(self, goal: str):
        self.store.execute(
            "INSERT INTO tasks (goal, status) VALUES (?, ?)",
            (goal, "in_progress")
        )

    def update(self, goal: str, last_step: str):
        self.store.execute(
            "UPDATE tasks SET last_step = ? WHERE goal = ? AND status = 'in_progress'",
            (last_step, goal)
        )

    def complete(self, goal: str):
        self.store.execute(
            "UPDATE tasks SET status = 'completed' WHERE goal = ?",
            (goal,)
        )

    def current_task(self):
        rows = self.store.fetchall(
            "SELECT * FROM tasks WHERE status = 'in_progress' ORDER BY id DESC LIMIT 1"
        )
        return rows[0] if rows else None
