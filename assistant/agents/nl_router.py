# assistant/agents/nl_router.py

import json
import requests
from assistant.agents.local_llm import LocalLLM
from assistant.config.settings import settings
from assistant.utils.logger import get_logger

log = get_logger(__name__)


class NLRouter:
    """
    Natural Language Router.

    Purpose:
    - Handle free-form, conversational, ambiguous input
    - Decide whether user is asking:
        * a question
        * a multi-step task
        * a follow-up
    - Produce a structured response for the coordinator

    This agent NEVER executes commands.
    """

    SYSTEM_PROMPT = """
You are Leo, a local Linux AI assistant.

Your job:
- Understand the user's intent
- Decide what the user wants
- If the user wants an action, produce a clear, specific English instruction
- The instruction must be detailed enough to be converted into a single bash command 

Output MUST be valid JSON with one of the following shapes:

1) Task:
{
  "type": "task",
  "instruction": "<precise natural language instruction>"
}

2) Conversation:
{
  "type": "chat",
  "response": "<friendly response>"
}

Be concise. Do not hallucinate system actions.
"""
    def __init__(self):
        LocalLLM.load(settings.LOCAL_LLM_PATH)

    def route(self, user_text: str) -> dict:
        log.info("[NLRouter] Routing text: %s", user_text)

        payload = {
            "model": settings.LLM_MODEL,
            "prompt": f"{self.SYSTEM_PROMPT}\nUser: {user_text}\nAssistant:",
            "stream": False,
        }

        try:
            r = requests.post(
                settings.OLLAMA_URL,
                json=payload,
                timeout=120,
            )
            r.raise_for_status()
        except Exception as e:
            log.error("LLM request failed: %s", e)
            return {
                "type": "chat",
                "response": "I'm having trouble thinking right now."
            }

        raw = r.json().get("response", "").strip()
        log.debug("[NLRouter] Raw LLM output: %s", raw)

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            log.warning("LLM returned non-JSON, falling back to chat")
            return {
                "type": "chat",
                "response": raw
            }
