import os, subprocess, shlex
from assistant.agents.safety import SafetyAgent
from assistant.agents.package_manager import PackageManagerAgent
from assistant.agents.process_monitor import ProcessMonitorAgent
from assistant.agents.intent_recognition import Intent
from assistant.utils.logger import get_logger

log = get_logger(__name__)

class ActionExecutionAgent:
    def __init__(self, ask_confirmation_callable):
        self.safety = SafetyAgent()
        self.pkg = PackageManagerAgent()
        self.mon = ProcessMonitorAgent()
        self.ask_confirm = ask_confirmation_callable  # function(text) -> bool

    def run(self, intent: Intent) -> str:
        if intent.name == "check_disk":
            return self.mon.disk_usage()
        if intent.name == "check_memory":
            return self.mon.memory()
        if intent.name == "check_installed" and intent.package:
            return f"{intent.package} installed: {self.pkg.is_installed(intent.package)}"
        if intent.name == "install_package" and intent.package:
            if self.pkg.is_installed(intent.package):
                return f"{intent.package} is already installed."
            argv = ["sudo", "apt-get", "install", "-y", intent.package]
            if not self.safety.is_safe(argv[1:]):  # check "apt-get"
                return "Command rejected by Safety Agent."
            if self.safety.needs_confirmation(argv[1:]):
                if not self.ask_confirm(f"Install {intent.package}?"):
                    return "Installation cancelled."
            out = self.pkg.install(intent.package)
            return out.stdout

        if intent.name == "svc_status" and intent.service:
            return self._safe_run(["systemctl", "status", intent.service, "--no-pager"])
        if intent.name in {"svc_start","svc_stop","svc_restart"} and intent.service:
            verb = intent.name.split("_")[1]
            argv = ["systemctl", verb, intent.service]
            if self.safety.needs_confirmation(argv):
                if not self.ask_confirm(f"{verb.capitalize()} service {intent.service}?"):
                    return "Action cancelled."
            return self._safe_run(argv)

        if intent.name == "open_app" and intent.app:
            # Try to run in background
            cmd = f"nohup {shlex.quote(intent.app)} >/dev/null 2>&1 &"
            return self._safe_run(["bash", "-lc", cmd])

        if intent.name == "speak_text" and intent.app:
            return intent.app

        return "I don't have an action for that yet."

    def _safe_run(self, argv: list[str]) -> str:
        if not self.safety.is_safe(argv):
            return "Command rejected by Safety Agent."
        r = subprocess.run(argv, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return r.stdout or "(no output)"
