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
    url: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    query: Optional[str] = None
    index: Optional[int] = None


class IntentRecognitionAgent:
    def parse(self, text: str) -> Optional[Intent]:
        t = text.lower().strip()
        t = re.sub(r"[^\w\s\-\._@/:]", " ", t)

        # Package management intents
        m = re.match(r"(?:install|setup|add)\s+([a-z0-9\-\._+:]+)(?:\s+version\s+([^\s]+))?", t)
        if m:
            pkg = m.group(1)
            ver = m.group(2)
            return Intent(name="install_package", package=pkg, extra=ver)

        m = re.match(r"(?:is|check if|is there)\s+([a-z0-9\-\._]+)\s+(?:installed|present)?", t)
        if m:
            return Intent(name="check_installed", package=m.group(1))

        m = re.match(r"(?:policy|apt policy)\s+([a-z0-9\-\._]+)", t)
        if m:
            return Intent(name="pkg_policy", package=m.group(1))

        if "disk" in t or "storage" in t:
            if "cleanup" in t or "save space" in t or "free space" in t:
                return Intent(name="disk_cleanup")
            return Intent(name="check_disk")
        if "memory" in t or "ram" in t:
            return Intent(name="check_memory")

        m = re.match(r"(?:status|start|stop|restart|enable|disable)\s+([a-zA-Z0-9@.\-_]+)", t)
        if m:
            verb = t.split()[0]
            return Intent(name=f"svc_{verb}", service=m.group(1))

        m = re.match(r"kill\s+pid\s+(\d+)", t)
        if m:
            return Intent(name="kill_pid", pid=int(m.group(1)))
        m = re.match(r"kill\s+([a-z0-9\-\._]+)", t)
        if m:
            return Intent(name="kill_name", extra=m.group(1))

        m = re.match(r"top(?:\s+(\d+))?", t)
        if m:
            n = int(m.group(1)) if m.group(1) else 10
            return Intent(name="top_processes", count=n)

        # GUI / App intents
        m = re.match(r"(?:open|go to|visit)\s+([^\s]+)", t, re.IGNORECASE)
        if m:
            url = m.group(1)

            if url.startswith("http://") or url.startswith("https://"):
                return Intent(name="open_url", url=url)

            elif re.match(r".+\.[a-zA-Z]{2,}(/.*)?$", url):
                return Intent(name="open_url", url="https://" + url)

        m = re.match(r"(?:open|launch|start)\s+([a-z0-9\-\._]+)(?:\s+app|browser)?", t)
        if m:
            return Intent(name="open_app", extra=m.group(1))

        # Email intent
        m = re.match(r"(?:send|compose|mail)\s+to\s+([^\s]+@[^\s]+)\s+(.+)", t)
        if m:
            recipient = m.group(1)
            body = m.group(2)
            return Intent(
                name="compose_mail",
                recipient=recipient,
                body=body,
                subject="",  # subject can be added later if user specifies
            )

        # Search intents
        m = re.match(r"(?:search|find|look for)\s+(.+)", t)
        if m:
            query = m.group(1)
            return Intent(name="search_query", query=query)

        # Misc
        m = re.match(r"(?:say|speak|echo)\s+(.+)", t)
        if m:
            return Intent(name="speak_text", text=m.group(1))

        return None
