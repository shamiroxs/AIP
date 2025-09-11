# assistant/agents/intent_recognition.py
import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class Intent:
    name: str
    package: Optional[str] = None
    service: Optional[str] = None
    pid: Optional[int] = None
    count: Optional[int] = None
    text: Optional[str] = None
    extra: Optional[str] = None

class IntentRecognitionAgent:
    def parse(self, text: str) -> Optional[Intent]:
        t = text.lower().strip()
        # Remove common punctuation
        t = re.sub(r"[^\w\s\-\._@/:]", " ", t)

        # install <pkg> (optionally version)
        m = re.match(r"(?:install|setup|add)\s+([a-z0-9\-\._+:]+)(?:\s+version\s+([^\s]+))?", t)
        if m:
            pkg = m.group(1)
            ver = m.group(2)
            return Intent(name="install_package", package=pkg, extra=ver)

        # check if installed <pkg>
        m = re.match(r"(?:is|check if|is there)\s+([a-z0-9\-\._]+)\s+(?:installed|present)?", t)
        if m: return Intent(name="check_installed", package=m.group(1))

        # apt policy / search
        m = re.match(r"(?:policy|apt policy|search)\s+([a-z0-9\-\._]+)", t)
        if m:
            return Intent(name="pkg_policy", package=m.group(1))

        # disk / memory
        if "disk" in t or "storage" in t:
            if "cleanup" in t or "save space" in t or "free space" in t:
                return Intent(name="disk_cleanup")
            return Intent(name="check_disk")
        if "memory" in t or "ram" in t:   return Intent(name="check_memory")

        # service status: status|start|stop|restart <service>
        m = re.match(r"(?:status|start|stop|restart|enable|disable)\s+([a-zA-Z0-9@.\-_]+)", t)
        if m:
            verb = t.split()[0]
            return Intent(name=f"svc_{verb}", service=m.group(1))

        # process: kill pid <n>  or kill <processname>
        m = re.match(r"kill\s+pid\s+(\d+)", t)
        if m: return Intent(name="kill_pid", pid=int(m.group(1)))
        m = re.match(r"kill\s+([a-z0-9\-\._]+)", t)
        if m: return Intent(name="kill_name", extra=m.group(1))

        # top n processes
        m = re.match(r"top(?:\s+(\d+))?", t)
        if m:
            n = int(m.group(1)) if m.group(1) else 10
            return Intent(name="top_processes", count=n)

        # open app
        m = re.match(r"(?:open|launch|start)\s+([a-z0-9\-\._]+)", t)
        if m: return Intent(name="open_app", extra=m.group(1))

        # say/echo
        m = re.match(r"(?:say|speak|echo)\s+(.+)", t)
        if m: return Intent(name="speak_text", text=m.group(1))

        return None
