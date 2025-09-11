# assistant/agents/action_execution.py
import shlex
import subprocess
from assistant.agents.safety import SafetyAgent
from assistant.agents.package_manager import PackageManagerAgent
from assistant.agents.process_monitor import ProcessMonitorAgent
from assistant.agents.intent_recognition import Intent
from assistant.utils.logger import get_logger

log = get_logger(__name__)

class ActionExecutionAgent:
    def __init__(self, confirm_callable):
        self.safety = SafetyAgent()
        self.pkg = PackageManagerAgent()
        self.mon = ProcessMonitorAgent()
        self.ask_confirm = confirm_callable  # function(question_text) -> bool

    def run(self, intent: Intent) -> str:
        # Disk / Memory
        if intent.name == "check_disk":
            return self.mon.disk_usage()
        if intent.name == "check_memory":
            return self.mon.memory()

        # Top processes
        if intent.name == "top_processes":
            return self.mon.top_processes(n=int(intent.count or 10))

        # Kill pid
        if intent.name == "kill_pid" and intent.pid:
            if self.safety.needs_confirmation(["kill", str(intent.pid)]):
                if not self.ask_confirm(f"Kill process {intent.pid}? This is potentially destructive."):
                    return "Cancelled."
            return self.mon.kill_pid(intent.pid)

        if intent.name == "kill_name" and intent.extra:
            # find pids with pgrep
            p = subprocess.run(["pgrep", "-f", intent.extra], text=True, stdout=subprocess.PIPE)
            pids = [int(x) for x in p.stdout.split() if x.isdigit()]
            if not pids:
                return f"No processes matching {intent.extra}."
            # ask confirm once with list
            if self.safety.needs_confirmation(["kill"] + [str(x) for x in pids]):
                if not self.ask_confirm(f"Kill processes {pids}?"):
                    return "Cancelled."
            outs = [self.mon.kill_pid(pid) for pid in pids]
            return "\n".join(outs)

        # Package manager flows
        if intent.name == "check_installed" and intent.package:
            return f"{intent.package} installed: {self.pkg.is_installed(intent.package)}"

        if intent.name == "pkg_policy" and intent.package:
            return self.pkg.apt_policy(intent.package)

        if intent.name == "install_package" and intent.package:
            pkg = intent.package
            if self.pkg.is_installed(pkg):
                return f"{pkg} is already installed."
            if not self.pkg.apt_exists(pkg):
                return f"Package {pkg} not found in apt cache."
            free_mb = self.pkg.available_disk_mb("/")
            if free_mb < 200:
                return f"Low disk space: only {free_mb} MB free. Aborting install."
            if self.safety.needs_confirmation(["apt-get", "install", pkg]):
                if not self.ask_confirm(f"Install {pkg}?"):
                    return "Installation cancelled."

            # Stream the install output (return final collated string)
            out_lines = []
            for line in self.pkg.install(pkg, update_first=True):
                # depending on how long the output is this may be large; we append
                out_lines.append(line.rstrip("\n"))
                # Optionally log
                log.info("[apt] %s", line.rstrip("\n"))
            return "\n".join(out_lines)

        # Service controls
        if intent.name.startswith("svc_") and intent.service:
            verb = intent.name.split("_", 1)[1]
            argv = ["systemctl", verb, intent.service]
            # Validate with safety agent
            if not self.safety.is_safe(argv):
                return "Action rejected by Safety Agent."
            if self.safety.needs_confirmation(argv):
                if not self.ask_confirm(f"{verb.capitalize()} service {intent.service}?"):
                    return "Cancelled."
            r = subprocess.run(["sudo"] + argv if self.safety.is_admin_action(argv) else argv,
                               text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            return r.stdout or "(no output)"

        # Open app (nohup)
        if intent.name == "open_app" and intent.extra:
            cmd = f"nohup {shlex.quote(intent.extra)} >/dev/null 2>&1 &"
            r = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            return r.stdout or "Launched."

        if intent.name == "speak_text" and intent.text:
            return intent.text

        return "I don't have an action for that yet."
