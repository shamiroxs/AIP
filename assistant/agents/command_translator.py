from assistant.agents.local_llm import LocalLLM
from assistant.utils.logger import get_logger

log = get_logger(__name__)


class CommandTranslationAgent:
    """
    Translates a precise English instruction into a bash command.
    Uses a fine-tuned T5 model.
    """

    def translate(self, instruction: str) -> str:
        prompt = instruction
        log.info("[CommandTranslator] Translating: %s", instruction)

        cmd = LocalLLM.generate(prompt, max_new_tokens=128)
        return cmd.strip()
