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
    ]

    def observe(self, action: dict, output: str) -> dict:
        log.info("[Observer] Observing result of %s", action)

        lowered = output.lower()

        for kw in self.FAILURE_KEYWORDS:
            if kw in lowered:
                return {
                    "status": "failure",
                    "reason": kw,
                    "output": output,
                }

        return {
            "status": "success",
            "output": output,
        }
