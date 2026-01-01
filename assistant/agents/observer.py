# assistant/agents/observer.py

from assistant.utils.logger import get_logger

log = get_logger(__name__)


class ObserverAgent:
    """
    Observes action execution output and determines success or failure.
    """

    FAILURE_KEYWORDS = [
        "error",
        "failed",
        "not found",
        "permission denied",
        "unable",
        "no such file",
    ]

    def observe(self, command: str, output: str) -> dict:
        log.info("[Observer] Observing result of %s", command)

        lowered = output.lower()

        for kw in self.FAILURE_KEYWORDS:
            if kw in lowered:
                return {
                    "status": "failure",
                    "reason": kw,
                    "command": command,
                    "output": output,
                }

        return {
            "status": "success",
            "command": command,
            "output": output,
        }
