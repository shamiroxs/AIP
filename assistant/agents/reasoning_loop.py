# assistant/agents/reasoning_loop.py

from assistant.utils.logger import get_logger
from assistant.agents.intent_recognition import Intent
from assistant.agents.task_planner import TaskPlannerAgent
from assistant.agents.observer import ObserverAgent

log = get_logger(__name__)


class ReasoningLoop:
    """
    Implements a ReAct-style loop:
    Plan -> Act -> Observe -> Replan
    """

    def __init__(self, executor, confirmer):
        """
        executor: ActionExecutionAgent
        confirmer: confirmation callable
        """
        self.executor = executor
        self.confirmer = confirmer
        self.planner = TaskPlannerAgent()
        self.observer = ObserverAgent()

    def run(self, goal: str) -> str:
        plan = self.planner.plan(goal)

        if not plan.get("steps"):
            return "I couldn't figure out how to do that safely."

        results = []

        for step in plan["steps"]:
            action = step.get("action")
            target = step.get("target")

            intent = self._intent_from_step(action, target)
            if not intent:
                log.warning("Unknown planned step: %s", step)
                continue

            log.info("[Reasoning] Executing step: %s", intent)

            output = self.executor.run(intent)
            results.append(output)

            observation = self.observer.observe(step, output)

            if observation["status"] == "failure":
                log.warning("[Reasoning] Step failed: %s", observation["reason"])
                return (
                    f"I tried to '{action} {target}', but it failed.\n"
                    f"Reason: {observation['reason']}"
                )

        return "\n".join(results)

    def _intent_from_step(self, action: str, target: str) -> Intent | None:
        """
        Maps planner steps to Intent objects.
        """
        if action == "install_package":
            return Intent(name="install_package", package=target)

        if action == "check_installed":
            return Intent(name="check_installed", package=target)

        if action == "open_app":
            return Intent(name="open_app", extra=target)

        if action == "check_disk":
            return Intent(name="check_disk")

        return None
