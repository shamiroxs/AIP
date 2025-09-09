import subprocess

class PackageManagerAgent:
    def is_installed(self, pkg: str) -> bool:
        r = subprocess.run(["dpkg", "-s", pkg], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return r.returncode == 0

    def install(self, pkg: str) -> subprocess.CompletedProcess:
        # uses sudo if available; you can configure sudoers later for NOPASSWD if desired
        return subprocess.run(["sudo", "apt-get", "install", "-y", pkg], text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def search_policy(self, pkg: str) -> subprocess.CompletedProcess:
        return subprocess.run(["apt-cache", "policy", pkg], text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
