# assistant/coordinator.py
from assistant.agents.response import ResponseAgent
from assistant.agents.intent_recognition import IntentRecognitionAgent
from assistant.agents.intent_recognition import Intent
from assistant.agents.action_execution import ActionExecutionAgent
from assistant.agents.confirm_agent import ConfirmAgent
from assistant.agents.gui_agent import GUIAgent
from assistant.agents.nl_router import NLRouter
from assistant.config.settings import settings
from assistant.utils.logger import get_logger
from assistant.agents.command_translator import CommandTranslationAgent
from assistant.agents.observer import ObserverAgent

from typing import Optional
import json
import time

log = get_logger(__name__)

class Coordinator:
    def __init__(self):
        self.resp = ResponseAgent()
        self.intent = IntentRecognitionAgent()
        self.confirm = ConfirmAgent()
        self.gui_agent = GUIAgent()
        self.nlrouter = NLRouter()
        self.exec = ActionExecutionAgent(self._confirm_voice)
        self.cmd_translator = CommandTranslationAgent()
        self.observer = ObserverAgent()
        self._retried_commands = set()


    def handle_text(self, text: str):
        text = text.strip()
        log.info("[Heard] %s", text)
        # wake word gating
        if not text.lower().startswith(settings.WAKE_WORD + " "):
            return  # ignore non-wake phrases
        command = text[len(settings.WAKE_WORD)+1:].strip()
        if not command:
            self.resp.say("Yes?")
            return
        it = self.intent.parse(command)

        if it is None or it.name == "unknown":
            log.info("[Coordinator] Unknown intent — routing to NLRouter")
            self._handle_unknown_with_llm(text)
            return
        '''
        if not it:
            self.resp.say("I didn't understand that command yet.")
            return
        '''
        result = self.exec.run(it)
        # Trim overly long outputs for TTS
        if isinstance(result, str) and len(result) > 500:
            # speak short confirmation and print details to console
            self.resp.say("Done. Output is long; see console for details.")
            print(result)
        else:
            self.resp.say(result if isinstance(result, str) else str(result))
    
    # ----- NLRouter handling (NEW) -----
    def _handle_unknown_with_llm(self, text: str):
        route = self.nlrouter.route(text)

        rtype = route.get("type")

        if rtype == "chat" or rtype == "conversation":
            self.resp.say(route.get("response", ""))

        elif rtype == "task" or rtype == "Task":
            goal = route.get("commands")
            
            if goal is None:
                self.resp.say(f"I don't understand that.")
                return
            self.resp.say(f"I understand. You want to {goal}.")
            confirmed = self._confirm_voice(f"Should I proceed to {goal}?")
            if not confirmed:
                self.resp.say("Okay, cancelled.")
                return
            for cmd in goal:
                log.info("[Coordinator] executing %s", cmd)
                output = self.exec.run_raw_command(cmd) or ""

                observation = self.observer.observe(cmd, output)

                if observation["status"] == "failure":

                    # If we've already retried this command once → stop
                    if cmd in self._retried_commands:
                        self.resp.say("That command failed again. Stopping to avoid harm.")
                        return
                    self.resp.say("Something went wrong. Let me try to fix it.")

                    replanned = self._replan(cmd, observation["output"])
                    if not replanned:
                        self.resp.say("I couldn't safely recover. Stopping.")
                        return

                    for new_cmd in replanned:
                        log.info("[Coordinator] recovery executing %s", new_cmd)
                        out = self.exec.run_raw_command(new_cmd)
                        if out:
                            self.resp.say(out)

                    # Mark this command as retried
                    self._retried_commands.add(cmd)

                    self.resp.say("Trying again now.")

                    # 🔁 RETRY the original command
                    retry_output = self.exec.run_raw_command(cmd) or ""
                    retry_obs = self.observer.observe(cmd, retry_output)

                    if retry_obs["status"] == "failure":
                        self.resp.say("It still failed after recovery. Stopping.")
                        return

                    # Success after retry
                    if retry_output:
                        self.resp.say(retry_output)
                        output = ""

                if output:
                    self.resp.say(output)

            self.resp.say("Done.")
            """
            goal = route.get("instruction")
            if goal is None:
                goal = route.get("command")
                if goal is None:
                    goal = route.get("result")
                    return
            self.resp.say(f"I understand. You want to {goal}.")
            '''
            confirmed = self._confirm_voice(f"Should I proceed to {goal}?")
            if not confirmed:
                self.resp.say("Okay, cancelled.")
                return
            '''
            # Step 2: Translate instruction → bash
            for g in goal:
                cmd = self.cmd_translator.translate(g)
                log.info("[Coordinator] command executing %s", cmd)
                result = self.exec.run_raw_command(cmd)
                if result:
                    self.resp.say(result)
            '''
            # Safety confirmation
            confirmed = self._confirm_voice(f"I will run: {cmd}. Proceed?")
            if not confirmed:
                self.resp.say("Okay, not running it.")
                return
            '''
            # Execute
            
            self.resp.say("Done.")
        """

        else:
            log.warning("[Coordinator] Unknown router output: %s", route)
            self.resp.say("I'm not sure how to handle that yet.")

    def _summarize_proposed_intent(self, intent: Intent, meta: dict) -> str:
        """
        Make a compact human-friendly summary of the proposed action and meta (confidence/reasons).
        """
        parts = []
        parts.append(f"Proposed action: {intent.name}")
        if intent.package:
            parts.append(f"Package: {intent.package}")
        if intent.service:
            parts.append(f"Service: {intent.service}")
        if intent.extra:
            extra = str(intent.extra)
            if len(extra) > 200:
                extra = extra[:200] + "..."
            parts.append(f"Details: {extra}")
        # include confidence if present
        conf = meta.get("confidence") or meta.get("confidence", None)
        if conf:
            parts.append(f"Confidence: {conf:.2f}")
        reasons = meta.get("reasons")
        if reasons:
            parts.append(f"Notes: {'; '.join(map(str,reasons))}")
        summary = ". ".join(parts)
        return summary

    def _clean_for_tts(self, s: str) -> str:
        s = s.replace("{", "").replace("}", "")
        s = s.replace("[", "").replace("]", "")
        s = s.replace("```", "")
        s = s.replace("*", "")
        s = s.replace("\n", "")
        return s.strip()[:250]


    def _confirm_voice(self, question: str) -> bool:
        # Speak the question and then listen for yes/no using ConfirmAgent
        self.resp.say(question)
        val = self.confirm.ask_confirm(question, timeout=6.0)
        log.info("[Confirm result] %s", val)
        if val is None:
            # fallback to keyboard + console
            self.resp.say("I didn't hear a clear response. Please type yes or no.")
            try:
                print("[Type yes/no then Enter] ", end="", flush=True)
                ans = input().strip().lower()
                return ans in {"y", "yes"}
            except Exception:
                return False
        return val

    def _replan(self, failed_cmd: str, error_output: str) -> Optional[list]:
            prompt = f"""
        The following shell command failed:

        Command:
        {failed_cmd}

        Error output:
        {error_output}
        """

            route = self.nlrouter.route(prompt)
            print(route)
            rtype = route.get("type")

            if rtype == "chat" or rtype == "conversation":
                log.warning("[Replan aborted] %s", route.get("response"))
                self.resp.say(route.get("response", ""))
                return None

            if rtype == "task":
                return route.get("commands")

            return None

