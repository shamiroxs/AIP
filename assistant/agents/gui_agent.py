import subprocess
import os
import time
import shutil

class GUIAgent:
    def __init__(self):
        self.display = os.environ.get("DISPLAY", ":0")

    # ------------------------
    # Application control
    # ------------------------
    def open_app(self, app_name):
        """Open an application using xdg-open or directly by name"""
        try:
            subprocess.Popen([app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            return f"Opened application: {app_name}"
        except FileNotFoundError:
            return f"Application not found: {app_name}"

    def open_url(self, url):
        """Open a URL in the default browser"""
        subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Opened URL: {url}"

    # ------------------------
    # Window control
    # ------------------------
    def focus_window(self, name):
        """Focus window by name"""
        try:
            subprocess.run(["wmctrl", "-a", name], check=True)
            return f"Focused window: {name}"
        except subprocess.CalledProcessError:
            return f"Window not found: {name}"

    def list_windows(self):
        """List all windows"""
        result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True)
        return result.stdout.strip()

    # ------------------------
    # Input simulation
    # ------------------------
    def type_text(self, text):
        """Type text into the active window"""
        subprocess.run(["xdotool", "type", "--delay", "100", text])
        return f"Typed text: {text}"

    def key_press(self, key):
        """Simulate key press"""
        subprocess.run(["xdotool", "key", key])
        return f"Pressed key: {key}"

    def mouse_click(self, button=1):
        """Simulate mouse click (1=left, 2=middle, 3=right)"""
        subprocess.run(["xdotool", "click", str(button)])
        return f"Mouse click button {button}"

    # ------------------------
    # Screenshots
    # ------------------------

    def _ensure_scrot_installed(self):
        """Check and install scrot if missing"""
        if shutil.which("scrot") is None:
            print("⚠️ scrot not found. Attempting installation...")
            try:
                subprocess.run(["sudo", "apt", "install", "-y", "scrot"], check=True)
                print("✅ scrot installed successfully.")
            except subprocess.CalledProcessError:
                return False
        return True


    def screenshot(self, filename="screenshot.png"):
        """Take screenshot with scrot"""
        if not self._ensure_scrot_installed():
            return "❌ Failed to install scrot. Cannot take screenshot."
        subprocess.run(["scrot", filename])
        return f"📸 Screenshot saved: {filename}"
