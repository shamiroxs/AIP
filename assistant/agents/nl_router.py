# assistant/agents/nl_router.py

import json
import requests
import re
from assistant.agents.local_llm import LocalLLM
from assistant.config.settings import settings
from assistant.utils.logger import get_logger

from assistant.memory.conversation_memory import ConversationMemory

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
    '''
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
    '''
    #new 1.5b prompt
    SYSTEM_PROMPT = """
You are a classifier.

Decide the user's intent.

Use "task" ONLY if the request requires executing one or more shell commands.
Use "chat" for questions, explanations, comparisons, or conversation.

Questions are ALWAYS chat.
If the intent is "task", output ALL required actions in the order they must be executed.

Output valid JSON only, No other explanations before or after the JSON.

1) Task:
{"type":"task","commands":["<shell command 1", "<shell command 2">, "<shell command N">]}

2) Chat:
{"type":"chat","response":"<answer>"}
"""


    def __init__(self):
        LocalLLM.load(settings.LOCAL_LLM_PATH)
        self.conversation_memory = ConversationMemory()

    def route(self, user_text: str) -> dict:
        log.info("[NLRouter] Routing text: %s", user_text)

        recent_context = self.conversation_memory.recent(limit=6)

        context_block = ""
        if recent_context:
            context_block = "Previous conversation:\n"
            for msg in recent_context:
                role = msg["role"].capitalize()
                context_block += f"{msg['role']}: {msg['content']}\n"

            context_block += "\n"

        prompt = (
            f"{self.SYSTEM_PROMPT}\n"
            
            f"User: {user_text}\n"
            f"Assistant:"
        )#f"{context_block}"

        payload = {
            "model": settings.LLM_MODEL,
            "prompt": prompt,
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

        def strip_code_fences(text: str) -> str:
            # Remove ```json ... ``` or ``` ... ```
            text = text.strip()
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            return text.strip()

        clean = strip_code_fences(raw)

        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            log.warning("LLM returned non-JSON, falling back to chat")
            return {
                "type": "chat",
                "response": raw
            }
