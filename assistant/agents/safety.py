from assistant.config.settings import settings

SAFE_BINARIES = {
    "df", "free", "systemctl", "ps", "pgrep", "bash", "sh", "grep", "awk", "sed",
    "xdg-open", "which", "apt-get", "apt-cache", "dpkg", "nohup"
}

PRIVILEGED = {"apt-get", "systemctl"}  # will require confirmation by default

class SafetyAgent:
    def __init__(self):
        self.require_confirm = settings.REQUIRE_CONFIRMATION_FOR_ROOT

    def is_safe(self, argv: list[str]) -> bool:
        if not argv: return False
        cmd = argv[0]
        return cmd in SAFE_BINARIES

    def needs_confirmation(self, argv: list[str]) -> bool:
        return self.require_confirm and argv and argv[0] in PRIVILEGED
