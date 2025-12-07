# assistant/agents/nl_router.py
import json
from assistant.agents.llm_agent import LLMAgent, LLMResponse
from assistant.security.llm_safety import LLMSafety
from assistant.agents.context_memory import ContextMemory
from assistant.config.settings import settings
from assistant.utils.logger import get_logger
from assistant.utils.response_formatter import format_for_speech, format_for_gui
from assistant.agents.intent_recognition import Intent

log = get_logger(__name__)

class NLRouter:
    def __init__(self):
        self.llm = LLMAgent()
        self.safety = LLMSafety()
        self.memory = ContextMemory()
        self.threshold = settings.SUGGESTION_CONFIDENCE_THRESHOLD

    def handle_unknown(self, text: str):
        """
        Main entry for unknown intents:
        - Get context
        - Ask LLM for natural answer
        - Ask LLM for command suggestion (optional)
        - Validate suggestion
        - Return a dict with keys:
            { "reply": str, "reply_speech": str, "proposed_intent": Intent|None, "proposed_meta": dict|None }
        """
        context = self.memory.get_context_for_query()
        log.info("[NLRouter] Getting LLM answer for user text: %s", text)
        ans: LLMResponse = self.llm.answer_query(text, context=context)
        reply = ans.text
        speech = format_for_speech(reply)
        gui_text = format_for_gui(reply)

        # Ask LLM for a proposed command/suggestion
        log.info("[NLRouter] Asking LLM to propose a command (if appropriate)")
        suggestion_resp: LLMResponse = self.llm.suggest_command(text, context=context)
        proposed_intent = None
        proposed_meta = None

        # Try parse JSON out of response
        try:
            payload = suggestion_resp.text.strip()
            # tolerate if LLM wrapped JSON in backticks or markdown; attempt to find first { ... }
            if "{" in payload:
                jstart = payload.find("{")
                jend = payload.rfind("}") + 1
                maybe_json = payload[jstart:jend]
                parsed = json.loads(maybe_json)
            else:
                parsed = {}
        except Exception as e:
            log.info("[NLRouter] No JSON suggestion parsed: %s", e)
            parsed = {}

        if parsed.get("propose_command"):
            # Validate via safety module
            ok, sanitized, reasons = self.safety.verify_and_sanitize_suggestion(parsed)
            proposed_meta = {"reasons": reasons, "ok": ok}
            if ok:
                # Map sanitized suggestion to Intent
                action = sanitized.get("action")
                args = sanitized.get("args", [])
                confidence = float(sanitized.get("confidence", 0.0))
                # Only propose actionable intent if confidence passes threshold
                if confidence >= self.threshold:
                    # Create Intent instance. Support install_package and others.
                    if action == "install_package" and args:
                        proposed_intent = Intent(name="install_package", package=args[0])
                        proposed_meta["confidence"] = confidence
                    elif action == "svc_action" and args:
                        proposed_intent = Intent(name=f"svc_{args[0]}", service=args[1] if len(args)>1 else None)
                        proposed_meta["confidence"] = confidence
                    else:
                        # Generic: put textual suggestion into Intent.extra for coordinator review.
                        proposed_intent = Intent(name="proposed_action", extra=json.dumps(sanitized))
                        proposed_meta["confidence"] = confidence
                else:
                    log.info("[NLRouter] Suggestion confidence too low (%s), will not propose intent.", confidence)
            else:
                log.info("[NLRouter] Suggestion failed safety checks: %s", reasons)

        # Record memory
        self.memory.add_turn(user_input=text, reply=reply, proposed=proposed_meta)

        return {
            "reply": gui_text,
            "reply_speech": speech,
            "proposed_intent": proposed_intent,
            "proposed_meta": proposed_meta
        }
