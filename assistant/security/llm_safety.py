# assistant/security/llm_safety.py
import re
from assistant.utils.logger import get_logger
from assistant.agents.verification_markov import MarkovVerifier

log = get_logger(__name__)

DANGEROUS_PATTERNS = [
    r"rm\s+-rf", r":\s*\(\s*\)\s*{\s*:\s*\|\s*:\s*&\s*};\s*:",  # fork bombs
    r"dd\s+if=", r">>\s*/dev/sd", r":\s*>/dev", r"mkfs\.", r"chmod\s+777\s+\/",
    r"curl\s+.*\|.*sh", r"wget\s+.*\|.*sh", r"bash\s+-c", r"sh\s+-c"
]

ALLOWED_ACTIONS = {"install_package", "svc_action", "open_url", "list_files", "check_disk"}

class LLMSafety:
    def __init__(self):
        self.detectors = [re.compile(p, re.IGNORECASE) for p in DANGEROUS_PATTERNS]
        self.verifier = MarkovVerifier()

    def _contains_danger(self, text: str) -> list:
        reasons = []
        for rx in self.detectors:
            if rx.search(text):
                reasons.append(f"Pattern matched: {rx.pattern}")
        return reasons

    def verify_and_sanitize_suggestion(self, suggestion: dict):
        """
        suggestion: expected JSON parsed from LLM.
        Returns tuple (is_safe: bool, sanitized_suggestion: dict, reasons: list).
        """
        reasons = []
        if not isinstance(suggestion, dict):
            reasons.append("Suggestion not a dict")
            return False, {}, reasons

        # Basic structure
        action = suggestion.get("action")
        if not action:
            reasons.append("No action present")
            return False, {}, reasons

        # Check allowed
        if action not in ALLOWED_ACTIONS and not action.startswith("install"):
            reasons.append(f"Action '{action}' not in allowed list")
            # we still continue to check content to give better reasons

        # Check for dangerous tokens in the raw explanation and args
        raw_text = (suggestion.get("explanation") or "") + " " + " ".join(map(str, suggestion.get("args", [])))
        danger_reasons = self._contains_danger(raw_text)
        reasons.extend(danger_reasons)
        if danger_reasons:
            log.info("[LLMSafety] Dangerous patterns detected: %s", danger_reasons)
            return False, {}, reasons

        # Run Markov verifier on args/command sequence
        score = self.verifier.score_sequence(" ".join(map(str, suggestion.get("args", []))))
        if score < 0:
            reasons.append("Markov verifier flagged sequence as anomalous")
            return False, {}, reasons

        # Construct sanitized suggestion: keep only allowed fields and safe args (alphanumeric, dash, dot)
        safe_args = []
        for a in suggestion.get("args", []):
            if isinstance(a, str) and re.match(r'^[\w\-\./:@]+$', a):
                safe_args.append(a)
            else:
                reasons.append(f"Argument rejected: {a}")

        sanitized = {
            "propose_command": True,
            "action": action,
            "args": safe_args,
            "explanation": suggestion.get("explanation", ""),
            "confidence": float(suggestion.get("confidence", 0.0))
        }

        ok = len(reasons) == 0
        return ok, sanitized, reasons
