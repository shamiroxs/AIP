# assistant/agents/task_planner.py

import json
import requests
from assistant.config.settings import settings
from assistant.utils.logger import get_logger

log = get_logger(__name__)


class TaskPlannerAgent:
    """
    Converts a high-level goal into an ordered list of steps.

    Output format:
    {
        "goal": "...",
        "steps": [
            {"action": "check_installed", "target": "vim"},
            {"action": "install_package", "target": "vim"}
        ]
    }
    """

    SYSTEM_PROMPT = """
You are Leo's task planner.

Rules:
- Break the user's goal into safe, minimal Linux actions
- Actions must map to known intents (install_package, check_disk, open_app, etc.)
- NEVER include raw shell commands
- Output valid JSON ONLY

Example:
Goal: "Install Vim"
Output:
{
  "goal": "Install Vim",
  "steps": [
    {"action": "check_installed", "target": "vim"},
    {"action": "install_package", "target": "vim"}
  ]
}
"""

    def plan(self, goal: str) -> dict:
        log.info("[Planner] Planning goal: %s", goal)

        payload = {
            "model": settings.LLM_MODEL,
            "prompt": f"{self.SYSTEM_PROMPT}\nGoal: {goal}\nPlan:",
            "stream": False,
        }

        try:
            r = requests.post(settings.OLLAMA_URL, json=payload, timeout=60)
            r.raise_for_status()
        except Exception as e:
            log.error("Planner LLM error: %s", e)
            return {"goal": goal, "steps": []}

        raw = r.json().get("response", "").strip()
        log.debug("[Planner] Raw output: %s", raw)

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            log.error("Planner returned invalid JSON")
            return {"goal": goal, "steps": []}
