import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class Intent:
    name: str
    package: Optional[str] = None
    service: Optional[str] = None
    app: Optional[str] = None

class IntentRecognitionAgent:
    def parse(self, text: str) -> Optional[Intent]:
        t = text.lower().strip()
        # install <pkg>
        m = re.match(r"(?:install|setup|add)\s+([a-z0-9\-\.]+)", t)
        if m: return Intent(name="install_package", package=m.group(1))
        # check if installed <pkg>
        m = re.match(r"(?:is|check if)\s+([a-z0-9\-\.]+)\s+(?:installed|present)", t)
        if m: return Intent(name="check_installed", package=m.group(1))
        # disk / memory
        if "disk" in t or "storage" in t: return Intent(name="check_disk")
        if "memory" in t or "ram" in t:   return Intent(name="check_memory")
        # service status: status|start|stop <service>
        m = re.match(r"(?:status|start|stop|restart)\s+([a-zA-Z0-9@.\-_]+)", t)
        if m:
            verb = t.split()[0]
            return Intent(name=f"svc_{verb}", service=m.group(1))
        # open app
        m = re.match(r"(?:open|launch|start)\s+([a-z0-9\-\._]+)", t)
        if m: return Intent(name="open_app", app=m.group(1))
        # say/echo
        m = re.match(r"(?:say|speak|echo)\s+(.+)", t)
        if m: return Intent(name="speak_text", app=m.group(1))
        return None
