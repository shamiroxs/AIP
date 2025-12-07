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

    # ----- NLRouter handling -----
    def _handle_unknown_with_llm(self, text: str):
        """
        Ask NLRouter (LLM) for a conversational reply and optional suggested intent.
        Present reply, then if a proposed_intent exists, ask for confirmation
        and (only if confirmed) pass to exec_agent for final safety/execution.
        """
        out = self.nlrouter.handle_unknown(text)
        reply = out.get("reply") or out.get("reply_speech") or "I don't have an answer."
        reply_speech = out.get("reply_speech") or reply
        proposed_intent: Optional[Intent] = out.get("proposed_intent")
        proposed_meta = out.get("proposed_meta") or {}

        # Present LLM reply: GUI + TTS + console
        try:
            # show in GUI if possible (simple notification using open_url or screenshot message)
            try:
                # Try to open a small GUI notification via xdg-open of a temporary file (best-effort)
                tmpfile = "/tmp/leo_llm_reply.txt"
                with open(tmpfile, "w", encoding="utf-8") as f:
                    f.write(reply)
                # Attempt to open the file in the default editor - best-effort
                #self.gui_agent.open_url("file://" + tmpfile)
            except Exception:
                log.debug("[Coordinator] GUI reply display failed (non-fatal)")

            # Speak short reply
            self.resp.say(reply_speech)

        except Exception as e:
            log.info("[Coordinator] Failed presenting reply: %s", e)

        # If LLM proposed an actionable intent, handle it
        if proposed_intent:
            log.info("[Coordinator] LLM proposed intent: %s meta=%s", proposed_intent, json.dumps(proposed_meta))
            # Summarize proposal for user confirmation
            summary = self._summarize_proposed_intent(proposed_intent, proposed_meta)
            # Voice ask & GUI fallback
            confirmed = self._confirm_proposal(summary)
            if not confirmed:
                self.resp.say("Okay, I will not run that command.")
                log.info("[Coordinator] User rejected proposed intent.")
                return

            # If confirmed by user, pass to exec_agent for final safety checks & execution.
            self.resp.say("Running the proposed action now.")
            try:
                result = self.exec_agent.run(proposed_intent)
                if isinstance(result, str) and len(result) > 500:
                    self.resp.say("Done. Output is long; see console.")
                    print(result)
                else:
                    self.resp.say(str(result))
            except Exception as e:
                log.exception("[Coordinator] Execution failed: %s", e)
                self.resp.say("Action failed during execution. Check logs.")

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
