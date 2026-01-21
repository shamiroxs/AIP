# assistant/agents/action_execution.py
import shlex
import subprocess, shutil
import time
import threading
from assistant.agents.safety import SafetyAgent
from assistant.agents.package_manager import PackageManagerAgent
from assistant.agents.process_monitor import ProcessMonitorAgent
from assistant.agents.intent_recognition import Intent
from assistant.utils.logger import get_logger
from assistant.utils.search import first_search_result, check_network
from assistant.agents.gui_agent import GUIAgent
from assistant.memory.task_memory import TaskMemory   # ✅ Layer 3

log = get_logger(__name__)
gui = GUIAgent()

class ActionExecutionAgent:
    def __init__(self, confirm_callable):
        """
        confirm_callable: function(question: str) -> bool
        """
        self.safety = SafetyAgent()
        self.pkg = PackageManagerAgent()
        self.mon = ProcessMonitorAgent()
        self.ask_confirm = confirm_callable
        self.task_memory = TaskMemory()   # ✅ Layer 3

    def run(self, intent: Intent) -> str:

        # System Info
        if intent.name == "check_disk":
            out = self.mon.disk_usage()
            self.task_memory.update(intent.description, "Checked disk usage")
            return out

        if intent.name == "check_memory":
            out = self.mon.memory()
            self.task_memory.update(intent.description, "Checked memory usage")
            return out

        # Process Monitor
        if intent.name == "top_processes":
            out = self.mon.top_processes(n=int(intent.count or 10))
            self.task_memory.update(intent.description, "Listed top processes")
            return out

        if intent.name == "kill_pid" and intent.pid:
            out = self.mon.kill_pid(intent.pid)
            self.task_memory.update(intent.description, f"Killed PID {intent.pid}")
            return out

        if intent.name == "kill_name" and intent.extra:
            p = subprocess.run(["pgrep", "-f", intent.extra], text=True, stdout=subprocess.PIPE)
            pids = [int(x) for x in p.stdout.split() if x.isdigit()]
            if not pids:
                return f"No processes matching {intent.extra}."

            outs = [self.mon.kill_pid(pid) for pid in pids]
            self.task_memory.update(
                intent.description,
                f"Killed processes: {pids}"
            )
            return "\n".join(outs)

        # Package Manager
        if intent.name == "check_installed" and intent.package:
            out = f"{intent.package} installed: {self.pkg.is_installed(intent.package)}"
            self.task_memory.update(intent.description, "Checked package installation")
            return out

        if intent.name == "pkg_policy" and intent.package:
            out = self.pkg.apt_policy(intent.package)
            self.task_memory.update(intent.description, "Checked package policy")
            return out

        if intent.name == "install_package" and intent.package:
            pkg = intent.package

            if self.pkg.is_installed(pkg):
                self.task_memory.update(intent.description, f"{pkg} already installed")
                return f"{pkg} is already installed."

            if self.pkg.apt_exists(pkg):
                out = "\n".join(self.pkg.install(pkg, update_first=True))
                self.task_memory.update(
                    intent.description,
                    f"Installed package {pkg}"
                )
                return out

            link = first_search_result(f"installing {pkg} on linux")
            if link:
                gui.open_url(link)
                self.task_memory.update(
                    intent.description,
                    f"Opened install guide for {pkg}"
                )
                return f"Opened install guide: {link}"

        # Service Controls
        if intent.name.startswith("svc_") and intent.service:
            verb = intent.name.split("_", 1)[1]
            argv = ["systemctl", verb, intent.service]
            r = subprocess.run(
                ["sudo"] + argv if self.safety.is_admin_action(argv) else argv,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            self.task_memory.update(
                intent.description,
                f"Service {intent.service}: {verb}"
            )
            return r.stdout or "(no output)"

        # Application Launch
        if intent.name == "open_app" and intent.extra:
            cmd = f"nohup {shlex.quote(intent.extra)} >/dev/null 2>&1 &"
            r = subprocess.run(["bash", "-lc", cmd])
            if r.returncode == 0:
                self.task_memory.update(
                    intent.description,
                    f"Launched application {intent.extra}"
                )
                return "Launched."
            return "Failed to launch."

        # URL / Search
        if intent.name == "open_url" and intent.url:
            gui.open_url(intent.url)
            self.task_memory.update(
                intent.description,
                f"Opened URL {intent.url}"
            )
            return f"opened url: {intent.url}"

        if intent.name == "search_query" and intent.query:
            link = first_search_result(intent.query)
            gui.open_url(link)
            self.task_memory.update(
                intent.description,
                f"Searched for {intent.query}"
            )
            return f"Searched and opened: {link}"

        # Voice Echo
        if intent.name == "speak_text" and intent.text:
            self.task_memory.update(intent.description, "Spoke text")
            return intent.text

        return "I don't have an action for that yet."

    def run_raw_command(self, cmd: str) -> str:
        if not cmd:
            return "No command provided."

        try:
            result = subprocess.run(
                ["bash", "-c", cmd],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=30
            )
            out = result.stdout.strip() or "(command executed successfully)"
            self.task_memory.update(
                "raw_command",
                f"Executed: {cmd}"
            )
            return out

        except subprocess.TimeoutExpired:
            self.task_memory.update("raw_command", "Command timed out")
            return "Command timed out."
