# assistant/agents/safety.py
from assistant.config.settings import settings

# Allowed command base names (without sudo). Only these are permitted to be executed.
SAFE_BINARIES = {
    "df", "free", "systemctl", "ps", "pgrep", "bash", "sh", "grep", "awk", "sed",
    "xdg-open", "which", "apt-get", "apt", "dpkg", "nohup", "kill", "pkill", "top"
}

# Commands that are considered privileged / admin-level (need sudo or sudoers)
PRIVILEGED_BINARIES = {"apt-get", "apt", "systemctl", "kill", "pkill"}

# For extra safety, allow only a limited subset of systemctl verbs
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
        # systemctl extra check: verb must be allowed
        if base == "systemctl" and len(argv) > 1:
            if argv[1] not in ALLOWED_SYSTEMCTL_VERBS:
                return False
        # kill can't be used on system critical pids by default (enforced in execution)
        return True

    def needs_confirmation(self, argv: list[str]) -> bool:
        if not argv: return True if argv and argv[0].split("/")[-1] in PRIVILEGED_BINARIES else False
        return False

    def is_admin_action(self, argv: list[str]) -> bool:
        return argv and argv[0].split("/")[-1] in PRIVILEGED_BINARIES
