# assistant/agents/safety.py
from assistant.config.settings import settings

SAFE_BINARIES = {
    "df", "free", "systemctl", "ps", "pgrep", "bash", "sh", "grep", "awk", "sed",
    "xdg-open", "which", "apt-get", "apt", "dpkg", "nohup", "kill", "pkill", "top"
}

PRIVILEGED_BINARIES = {"apt-get", "apt", "systemctl", "kill", "pkill"}
ALLOWED_SYSTEMCTL_VERBS = {"start", "stop", "restart", "status", "enable", "disable"}

class SafetyAgent:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.require_confirm = settings.REQUIRE_CONFIRMATION_FOR_ROOT

    def _is_allowed_binary(self, bin_name: str) -> bool:
        return bin_name in SAFE_BINARIES

    def is_safe(self, argv: list[str]) -> bool:
        if not argv: return False
        base = argv[0].split("/")[-1]
        if not self._is_allowed_binary(base):
            return False
        if base == "systemctl" and len(argv) > 1:
            if argv[1] not in ALLOWED_SYSTEMCTL_VERBS:
                return False
        return True

    def needs_confirmation(self, argv: list[str]) -> bool:
        if not argv: return True if argv and argv[0].split("/")[-1] in PRIVILEGED_BINARIES else False
        return False

    def is_admin_action(self, argv: list[str]) -> bool:
        return argv and argv[0].split("/")[-1] in PRIVILEGED_BINARIES
