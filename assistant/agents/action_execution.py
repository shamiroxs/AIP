# assistant/agents/action_execution.py
import shlex
import subprocess, shutil
from assistant.agents.safety import SafetyAgent
from assistant.agents.package_manager import PackageManagerAgent
from assistant.agents.process_monitor import ProcessMonitorAgent
from assistant.agents.intent_recognition import Intent
from assistant.utils.logger import get_logger
from assistant.utils.search import first_search_result, check_network
from assistant.agents.gui_agent import GUIAgent

log = get_logger(__name__)
gui = GUIAgent()

class ActionExecutionAgent:
    def __init__(self, confirm_callable):
        """
        confirm_callable: function(question: str) -> bool
        This is injected from GUI/Voice layer to handle user confirmations.
        """
        self.safety = SafetyAgent()
        self.pkg = PackageManagerAgent()
        self.mon = ProcessMonitorAgent()
        self.ask_confirm = confirm_callable

    def run(self, intent: Intent) -> str:

        # --- System Info ---
        if intent.name == "check_disk":
            return self.mon.disk_usage()
        if intent.name == "check_memory":
            return self.mon.memory()

        # --- Process Monitor ---
        if intent.name == "top_processes":
            return self.mon.top_processes(n=int(intent.count or 10))

        if intent.name == "kill_pid" and intent.pid:
            if self.safety.needs_confirmation(["kill", str(intent.pid)]):
                if not self.ask_confirm(f"Kill process {intent.pid}? This may disrupt your system."):
                    return "Cancelled."
            return self.mon.kill_pid(intent.pid)

        if intent.name == "kill_name" and intent.extra:
            p = subprocess.run(["pgrep", "-f", intent.extra], text=True, stdout=subprocess.PIPE)
            pids = [int(x) for x in p.stdout.split() if x.isdigit()]
            if not pids:
                return f"No processes matching {intent.extra}."
            if self.safety.needs_confirmation(["kill"] + [str(x) for x in pids]):
                if not self.ask_confirm(f"Kill processes {pids}?"):
                    return "Cancelled."
            outs = [self.mon.kill_pid(pid) for pid in pids]
            return "\n".join(outs)

        # --- Package Manager ---
        if intent.name == "check_installed" and intent.package:
            return f"{intent.package} installed: {self.pkg.is_installed(intent.package)}"

        if intent.name == "pkg_policy" and intent.package:
            return self.pkg.apt_policy(intent.package)

        if intent.name == "install_package" and intent.package:
            pkg = intent.package
            if self.pkg.is_installed(pkg):
                return f"{pkg} is already installed."

            free_mb = self.pkg.available_disk_mb("/")
            if free_mb < 200:
                return f"Low disk space: only {free_mb} MB free. Aborting install."

            net_result = check_network(pkg)
            if net_result is not True:
                return net_result

            # --- Try APT ---
            if self.pkg.apt_exists(pkg):
                if self.safety.needs_confirmation(["apt-get", "install", pkg]):
                    if not self.ask_confirm(f"Install {pkg} via apt?"):
                        return "Installation cancelled."
                return "\n".join(self.pkg.install(pkg, update_first=True))
            '''
            # --- Try Snap ---
            if shutil.which("snap"):
                snap_check = subprocess.run(["snap", "find", pkg], text=True, stdout=subprocess.PIPE)
                if pkg in snap_check.stdout:
                    if self.safety.needs_confirmation(["snap", "install", pkg]):
                        if not self.ask_confirm(f"Install {pkg} via snap?"):
                            return "Installation cancelled."
                    r = subprocess.run(["sudo", "snap", "install", pkg],
                                    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    return r.stdout or f"Installed {pkg} via snap."

            # --- Try Flatpak ---
            if shutil.which("flatpak"):
                flatpak_check = subprocess.run(["flatpak", "search", pkg], text=True, stdout=subprocess.PIPE)
                if pkg in flatpak_check.stdout:
                    if self.safety.needs_confirmation(["flatpak", "install", pkg]):
                        if not self.ask_confirm(f"Install {pkg} via flatpak?"):
                            return "Installation cancelled."
                    r = subprocess.run(["flatpak", "install", "-y", "flathub", pkg],
                                    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    return r.stdout or f"Installed {pkg} via flatpak."
            '''
            # --- Fallback: Open Browser ---
            search_query = f"installing {pkg} on linux"
            link = first_search_result(search_query)

            if link:
                gui.open_url(link)
                return f"Package {pkg} not found in apt. Opened install guide in browser: {link}"
            else:
                url = f"https://www.google.com/search?q={search_query}"
                gui.open_url(url)
                return f"Package {pkg} not found. Opened Google search instead: {url}"

        # --- Service Controls ---
        if intent.name.startswith("svc_") and intent.service:
            verb = intent.name.split("_", 1)[1]
            argv = ["systemctl", verb, intent.service]
            if not self.safety.is_safe(argv):
                return "Action rejected by Safety Agent."
            if self.safety.needs_confirmation(argv):
                if not self.ask_confirm(f"{verb.capitalize()} service {intent.service}?"):
                    return "Cancelled."
            r = subprocess.run(["sudo"] + argv if self.safety.is_admin_action(argv) else argv,
                               text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            return r.stdout or "(no output)"

        # --- Application Launch ---
        if intent.name == "open_app" and intent.extra:
            if shutil.which(intent.extra) is None:
                return f"Application '{intent.extra}' not found."

            cmd = f"nohup {shlex.quote(intent.extra)} >/dev/null 2>&1 &"
            r = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if r.returncode != 0:
                return f"Failed to launch: {r.stdout.strip()}"
            else:
                return "Launched."

        # --- Voice Output (Echo/Speak) ---
        if intent.name == "speak_text" and intent.text:
            return intent.text

        return "I don't have an action for that yet."
