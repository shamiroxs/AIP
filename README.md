# 🎙️ Leo (Version 1)

**Leo** is our Linux-based **voice (and text) assistant**, developed as part of our BTech final year project.
This is **Version 1**, with major improvements from the prototype (v0).

Leo can **listen to commands, check system status, manage processes, install packages (with confirmation), and control services** — while enforcing **safety checks** to avoid misuse.

---

## 🚀 New in Version 1

* ✅ Assistant renamed to **Leo**
* ✅ **ConfirmAgent** → Listens for short "yes/no" answers (3–6s) using Vosk. Falls back to console input if unclear/no audio.
* ✅ **Expanded Intents** in `intent_recognition.py`

  * Install with version (`leo install curl=7.81`)
  * Check package policy (`leo apt policy curl`)
  * Check process (`leo is firefox running`)
  * Kill PID safely (`leo kill pid 12345`)
  * Show top N processes (`leo top 5`)
  * Disk cleanup suggestion (`leo suggest cleanup`)
  * Service control (`leo start ssh.service`, `leo stop apache2.service`)
* ✅ **Safety Layer** (`safety.py`)

  * Only allows whitelisted binaries
  * Marks some actions as **admin-only**
* ✅ **Improved Package Manager** (`package_manager.py`)

  * Prechecks before install
  * Streams output live to user
* ✅ **Process Monitor** (`process_monitor.py`)

  * List services
  * Show top N processes
  * Safe kill (prevents killing system-critical PIDs)
* ✅ **Coordinator updates** (`assistant/coordinator.py`)

  * Uses **ConfirmAgent** + **ResponseAgent** → confirmation prompt is spoken first, then Leo listens.

---

## 📦 Requirements

* Linux (Debian/Ubuntu recommended)
* Python **3.9+**
* Virtual environment (`venv`)
* Microphone (for voice mode)
* System dependencies:

  * `ffmpeg`
  * `sox`
  * `portaudio`

---

## 🔧 Installation

```bash
# Clone the repo
git clone https://github.com/shamiroxs/AIP.git
cd AIP

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Usage

### 1. **Text Mode (easier for testing)**

Run Leo with direct text commands:

```bash
cd ~/AIP
source .venv/bin/activate

# Examples:
python -m assistant.main --text "leo check disk"
python -m assistant.main --text "leo check memory"
python -m assistant.main --text "leo top 5"
python -m assistant.main --text "leo apt policy curl"
python -m assistant.main --text "leo is curl installed"
python -m assistant.main --text "leo install sl"      # safe package to test install
python -m assistant.main --text "leo status ssh.service"
python -m assistant.main --text "leo kill pid 99999"  # test with dummy pid
```

⚠️ **Do not try to kill important system PIDs (≤100).**

---

### 2. **Voice Mode (mic)**

Run Leo with microphone input:

```bash
./run.sh
```

Then say:

```
leo check disk
leo check memory
leo install sl
```

Leo will:

* Ask for confirmation (voice preferred, console fallback)
* Stream outputs in real time

---

## 🔐 Sudoers Setup (Important)

Some actions (like installing packages or controlling services) need `sudo`.
Instead of entering your password every time, you can allow Leo **specific commands without a password**.

⚠️ **Do NOT grant unrestricted rights.** Only allow the commands you fully understand.

Create file:

```bash
sudo visudo -f /etc/sudoers.d/voice-assistant
```

Paste (replace `yourusername` with your Linux username):

```
# voice-assistant: allow specific apt-get and systemctl actions for Leo
# WARNING: this allows package install and service control via assistant
yourusername ALL=(ALL) NOPASSWD: /usr/bin/apt-get, /usr/bin/apt, /bin/systemctl, /bin/kill, /usr/bin/kill
```

Set permissions:

```bash
sudo chmod 440 /etc/sudoers.d/voice-assistant
sudo -l -U yourusername
```

✅ Test with a safe command (e.g., installing `sl`).

---

## 🧪 What to Test Now

* Disk & memory checks
* Top N processes
* Package policy check
* Install `sl` (safe, small package)
* Service status (e.g., `ssh.service`)
* Dummy PID kill test

---

## ⚠️ Problems / Things to Improve

* [ ] Speech recognition accuracy
* [ ] Text-to-speech quality
* [ ] Add a dashboard (UI for monitoring commands + logs)

---

## 🛠️ Next Steps

* Provide **wrapper scripts** for safer sudoers configuration
* Add stricter argument validation
* Expand Leo’s supported commands

---

## 👨‍💻 Authors

* **Gopu Girish, Shamir Ashraf, Yadhu Krishnan PU**
* GitHub: [shamiroxs/AIP](https://github.com/shamiroxs/AIP)
