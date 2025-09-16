# 🎙️ Leo (Version 2)

**Leo** is our Linux-based **voice + text assistant**, developed as part of our BTech final year project.

This is **Version 2**, building on top of V1 with major **environment setup tools** and a new **GUI Agent** for desktop automation.

---

## 🚀 What’s New in Version 2

* ✅ **Setup Scripts**

  * `setup_env.sh` → Installs all Debian packages, sets up Python virtual environment, and installs Python dependencies.
  * `check_env.sh` → Verifies system environment:

    * Confirms X11 session is running
    * Checks microphone availability
    * Checks required tools (`xdotool`, `wmctrl`, `sox`, etc.)

* ✅ **GUI Agent (X11 Automation)**

  * Launch apps (`xdg-open`, `subprocess.Popen`)
  * Focus and control windows (`xdotool`, `wmctrl`)
  * Type text into active apps
  * Simulate key presses and mouse actions
  * Open URLs in the default browser
  * Take screenshots for debugging/feedback

* ✅ **New Intents**

  * `open_url` → open a webpage
  * `compose_mail` → quick email drafting
  * `search_query` → web search for queries

* ✅ **Improved Package Install**

  * If `apt install` fails (package not found):

    * Leo searches the web for install guides.
    * Automatically opens the first result in your browser.
    * Falls back to Google search if no guide found.

---

## 📦 Requirements

* Debian **11/12** (X11 session required – **NOT Wayland**)
* Python **3.9+**
* Microphone + working audio (ALSA/PulseAudio)
* Sudo privileges for installing system packages

---

## 🔧 Installation (Beginner-Friendly)

### 1. Clone the repo

```bash
git clone https://github.com/shamiroxs/AIP.git
cd AIP
```

### 2. Run the setup script

```bash
chmod +x setup_env.sh
./setup_env.sh
```

This will:

* Install required Debian packages (`ffmpeg`, `sox`, `portaudio19-dev`, `xdotool`, `wmctrl`, etc.)
* Create a Python virtual environment
* Install all Python dependencies from `requirements.txt`

### 3. Check your environment

```bash
chmod +x check_env.sh
./check_env.sh
```

This script will tell you if:

* You are running in **X11** (✅ required for GUI automation)
* Your microphone is detected
* Required tools are installed

⚠️ **If you see “Wayland” instead of “X11” → Log out and select “X11 session” before running Leo.**

---

## ▶️ Usage

### Text Mode (safe for testing)

```bash
source .venv/bin/activate
python -m assistant.main --text "leo mail to user@mail.com hello sam"
python -m assistant.main --text "leo search python file handling"
```

### Voice Mode (mic)

```bash
./run.sh
```

Then say:

```
leo open firefox
leo mail to user@mail.com hello sam
```

Leo will:

* Confirm via voice/console
* Run system commands OR control desktop apps

---

## 🖥️ GUI Agent Examples

```bash
# Open YouTube
python -m assistant.main --text "leo open youtube.com"

# Compose an email draft
python -m assistant.main --text "leo mail to test@mail.com hey, checking Leo V2!"

# Search Google
python -m assistant.main --text "leo search install python on debian"
```

---

## 🔐 Sudoers Setup (Same as V1)

If you haven’t already done this in V1:
Grant Leo **specific sudo rights** for `apt`, `systemctl`, and `kill`. (See [V1 README section](./README_V1.md))

---

## 🧪 Things to Test in V2

* Environment checks (`./check_env.sh`)
* GUI commands (open website, search, mail)
* Fallback: try installing a fake package → Leo should open browser with install guide
* Voice confirmations (yes/no)

---

## ⚠️ Known Issues / To Improve

* GUI agent only works on **X11**
* Limited window handling (sometimes focus fails if multiple apps open)
* Voice recognition still inconsistent in noisy environments

---

## 👨‍💻 Authors

* **Gopu Girish, Shamir Ashraf, Yadhu Krishnan PU**
* GitHub: [shamiroxs/AIP](https://github.com/shamiroxs/AIP)

---

👉 **Teammates:** Please **make sure you are on X11 before testing GUI features**. Run `echo $XDG_SESSION_TYPE`. If it says `wayland`, log out and choose `X11 session` from your login screen.