# assistant/agents/llm_agent.py
import json
import time
import requests
from assistant.config.settings import settings
from assistant.data.prompts import PROMPT_SYSTEM, PROMPT_ANSWER_TEMPLATE
from assistant.utils.logger import get_logger
from typing import Dict, Any, Optional

log = get_logger(__name__)

class LLMResponse:
    def __init__(self, text: str, meta: Optional[Dict[str, Any]] = None):
        self.text = text
        self.meta = meta or {}

class MockLLM:
    """Simple deterministic fallback LLM used when no remote model is available."""
    def answer(self, prompt: str) -> LLMResponse:
        # Very conservative mock: do not propose commands automatically.
        text = "I can help explain Linux commands and suggest safe next steps. " \
               "Ask me to check disk usage or list processes, and I will suggest verified commands."
        return LLMResponse(text=text, meta={"model": "mock", "time_ms": 1})

    def suggest(self, prompt: str) -> LLMResponse:
        # Return an example JSON suggestion only if prompt clearly requests install
        if "install" in prompt.lower() and "firefox" in prompt.lower():
            sugg = {
                "propose_command": True,
                "action": "install_package",
                "args": ["firefox"],
                "explanation": "Install firefox via apt-get",
                "confidence": 0.6
            }
            return LLMResponse(text=json.dumps(sugg), meta={"model": "mock", "time_ms": 1})
        return LLMResponse(text="{}", meta={"model": "mock", "time_ms": 1})

class LLMAgent:
    def __init__(self):
        self.enabled = settings.LLM_ENABLED
        self.host = settings.LLM_HOST
        self.model = settings.LLM_MODEL_NAME
        self.timeout = settings.LLM_TIMEOUT_SECONDS
        # Use requests when contacting a running LLM server; otherwise use Mock.
        self._mock = MockLLM()

    def _build_prompt(self, user_text: str, context: str = "") -> str:
        return PROMPT_ANSWER_TEMPLATE.format(system_prompt=PROMPT_SYSTEM, context=context, user_input=user_text)

    def answer_query(self, text: str, context: str = "") -> LLMResponse:
        prompt = self._build_prompt(text, context)
        log.info("[LLM] answer_query - sending prompt (len=%d)", len(prompt))
        if not self.enabled:
            return self._mock.answer(prompt)
        try:
            # Attempt a generic HTTP POST to configured LLM host.
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": PROMPT_SYSTEM},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }

            r = requests.post(f"{self.host}/v1/chat/completions", json=payload, timeout=self.timeout)


            print("\n--- RAW LLM RESPONSE (answer_query) ---\n", r.text, "\n-----------------------\n")
            r.raise_for_status()
            body = r.json()
            txt = body["choices"][0]["message"]["content"]
            return LLMResponse(text=txt, meta={"model": self.model, "raw": body})
        except Exception as e:
            log.warning("[LLM] remote call failed: %s", e)
            return self._mock.answer(prompt)

    def suggest_command(self, text: str, context: str = "") -> LLMResponse:
        """
        Ask the LLM to propose a command in the JSON schema described in prompts.py.
        Returns LLMResponse where text may be JSON; caller must parse and validate.
        """
        prompt = self._build_prompt("Please propose a safe command (JSON) if appropriate:\n\n" + text, context)
        if not self.enabled:
            return self._mock.suggest(prompt)
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": PROMPT_SYSTEM},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }

            r = requests.post(f"{self.host}/v1/chat/completions", json=payload, timeout=self.timeout)

            r.raise_for_status()
            body = r.json()
            txt = body["choices"][0]["message"]["content"]

            return LLMResponse(text=txt, meta={"model": self.model, "raw": body})
        except Exception as e:
            log.warning("[LLM] remote suggest failed: %s", e)
            return self._mock.suggest(prompt)
