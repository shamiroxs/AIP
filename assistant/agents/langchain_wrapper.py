# assistant/agents/langchain_wrapper.py
"""
Minimal wrapper offering a small set of tools that can be invoked to supply
grounded information to an LLM. This is intentionally simple and runs locally.
"""

from assistant.agents.process_monitor import ProcessMonitorAgent
from assistant.agents.package_manager import PackageManagerAgent
from assistant.utils.logger import get_logger

log = get_logger(__name__)

class ToolRunner:
    def __init__(self):
        self.proc = ProcessMonitorAgent()
        self.pkg = PackageManagerAgent()

    def list_top(self, n=5):
        return self.proc.top_processes(n=n)

    def check_disk(self):
        return self.proc.disk_usage()

    def check_memory(self):
        return self.proc.memory()

    def package_policy(self, pkg: str):
        return self.pkg.apt_policy(pkg)

    # Utility to expose as a mapping for prompt descriptions
    def tools_map(self):
        return {
            "list_top": self.list_top,
            "check_disk": self.check_disk,
            "check_memory": self.check_memory,
            "package_policy": self.package_policy
        }
