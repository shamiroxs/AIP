# assistant/agents/process_monitor.py
import subprocess
from typing import Generator

class ProcessMonitorAgent:
    def disk_usage(self) -> str:
        r = subprocess.run(["df", "-h"], text=True, stdout=subprocess.PIPE)
        return r.stdout

    def memory(self) -> str:
        r = subprocess.run(["free", "-h"], text=True, stdout=subprocess.PIPE)
        return r.stdout

    def top_processes(self, n: int = 10) -> str:
        r = subprocess.run(["ps", "aux", "--sort=-%mem"], text=True, stdout=subprocess.PIPE)
        lines = r.stdout.splitlines()
        header = lines[0]
        return "\n".join([header] + lines[1:1+n])

    def kill_pid(self, pid: int) -> str:
        # Basic safety: do not kill pid 1 or current process or system-critical pids (<= 100)
        if pid <= 100:
            return f"Refusing to kill system PID {pid} (protected)."
        r = subprocess.run(["sudo", "kill", "-9", str(pid)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return r.stdout or f"kill returned {r.returncode}"

    def list_services(self, pattern: str | None = None) -> str:
        # list systemctl --type=service --all
        cmd = ["systemctl", "list-units", "--type=service", "--all", "--no-pager"]
        r = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = r.stdout
        if pattern:
            out = "\n".join([ln for ln in out.splitlines() if pattern in ln])
        return out
