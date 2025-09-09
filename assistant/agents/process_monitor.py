import subprocess

class ProcessMonitorAgent:
    def disk_usage(self) -> str:
        r = subprocess.run(["df", "-h"], text=True, stdout=subprocess.PIPE)
        return r.stdout

    def memory(self) -> str:
        r = subprocess.run(["free", "-h"], text=True, stdout=subprocess.PIPE)
        return r.stdout
