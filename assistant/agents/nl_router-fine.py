finetunned model only

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
- DO NOT execute commands
- Decide what the user wants at a high level

Output MUST be valid JSON with one of the following shapes:

1) Question:
{
  "type": "question",
  "answer": "<natural language answer>"
}

2) Task:
{
  "type": "task",
  "goal": "<high level goal>",
  "requires_system_actions": true
}

3) Conversation:
{
  "type": "chat",
  "response": "<friendly response>"
}

Be concise. Do not hallucinate system actions.
"""

    def __init__(self):
        # Load the local fine-tuned model once
        LocalLLM.load(settings.LOCAL_LLM_PATH)

    def route(self, user_text: str) -> dict:
        log.info("[NLRouter] Routing text: %s", user_text)

        prompt = (
            f"{self.SYSTEM_PROMPT}\n"
            f"User: {user_text}\n"
            f"Assistant:"
        )

        try:
            raw = LocalLLM.generate(prompt, max_new_tokens=300).strip()
            log.debug("[NLRouter] Raw LLM output: %s", raw)
        except Exception as e:
            log.exception("[NLRouter] LLM generation failed: %s", e)
            return {
                "type": "chat",
                "response": "I'm having trouble thinking right now."
            }

        # Attempt strict JSON parsing
        try:
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                raise ValueError("Parsed JSON is not an object")
            if "type" not in parsed:
                raise ValueError("Missing 'type' field")
            return parsed

        except Exception as e:
            log.warning("[NLRouter] Invalid JSON from LLM: %s", e)
            log.warning("[NLRouter] Falling back to chat response")

            # Safe fallback: treat raw text as chat
            return {
                "type": "chat",
                "response": self._clean_fallback(raw)
            }

    def _clean_fallback(self, text: str) -> str:
        """
        Clean raw model output for safe conversational fallback.
        """
        text = text.strip()
        # Avoid dumping long or malformed output to TTS
        if len(text) > 300:
            text = text[:300] + "..."
        # Remove obvious JSON debris
        for ch in ["{", "}", "[", "]", "`"]:
            text = text.replace(ch, "")
        return text or "Okay."
