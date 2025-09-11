# assistant/agents/package_manager.py
import subprocess
import shutil
from assistant.utils.logger import get_logger

log = get_logger(__name__)

class PackageManagerAgent:
    def __init__(self):
        pass

    def is_installed(self, pkg: str) -> bool:
        r = subprocess.run(["dpkg-query", "-W", "-f=${Status}", pkg], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return "install ok installed" in r.stdout

    def apt_policy(self, pkg: str) -> str:
        r = subprocess.run(["apt-cache", "policy", pkg], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return r.stdout

    def apt_exists(self, pkg: str) -> bool:
        out = self.apt_policy(pkg)
        return "Candidate:" in out and "Candidate: (none)" not in out

    def available_disk_mb(self, path: str = "/") -> int:
        total, used, free = shutil.disk_usage(path)
        return int(free / (1024*1024))

    def install(self, pkg: str, update_first: bool = True):
        """
        Return a generator that yields stdout lines (so caller can stream).
        """
        if update_first:
            # Do apt-get update first
            proc = subprocess.Popen(["sudo", "apt-get", "update"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                yield line
            proc.wait()

        cmd = ["sudo", "apt-get", "install", "-y", pkg]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            yield line
        proc.wait()
        yield f"[exit {proc.returncode}]"
