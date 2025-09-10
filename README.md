# 🎙️ AIP (Version 0)

A **voice-activated AI assistant** embedded into **Linux (Debian-based systems)**.  
This project is my **final year BTech project**, aiming to build an **autonomous AI system** that can execute commands, interact with the user, and manage system-level tasks using **natural language (voice or text)**.

---

## 🚀 Features (Version 0 Prototype)

- ✅ **Text & Voice Modes**  
  - Run via text input (terminal)  
  - Or use microphone for real-time voice commands  

- ✅ **Command Execution**  
  - Check system status (disk usage, memory usage)  
  - Run safe package/service actions with confirmation  

- ✅ **Agents Implemented**
  - **Voice Input Agent** → Captures voice commands  
  - **Intent Recognition Agent** → Parses user commands  
  - **Action Execution Agent** → Runs corresponding system commands  
  - **Response Agent** → Gives user feedback in text/voice  

- ✅ **Safety Layer**  
  - Prompts for confirmation before package installs or service changes  

---

## 📦 Requirements

- Linux Debian-based OS (tested on Ubuntu/Debian)
- Python **3.9+**
- `venv` (for virtual environment)
- Microphone (for voice mode)
- System dependencies:
  - `ffmpeg`
  - `sox`
  - `portaudio` (for voice input)

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

### 1. **Text Mode (No Mic)**

Run commands by passing text directly:

```bash
cd ~/voice-assistant
source .venv/bin/activate

# Examples
python -m assistant.main --text "assistant say hello"
python -m assistant.main --text "assistant check disk"
python -m assistant.main --text "assistant check memory"
python -m assistant.main --text "assistant is ffmpeg installed"
```

---

### 2. **Voice Mode (Mic)**

Run the assistant with microphone input:

```bash
./run.sh
```

Then say:

```
assistant check disk
assistant check memory
assistant say hello
```

For package installations or service actions, the assistant will **prompt in the terminal** for a yes/no confirmation. (Voice confirmation coming soon!)

---

## 📌 Roadmap

* [ ] Add **voice-based confirmation** for installs and service actions
* [ ] Improve **NLP model** for better intent recognition
* [ ] Add **context awareness** (check if software is already installed, available disk space, etc.)
* [ ] Implement more **agents**:

  * Package Manager Agent
  * Process Monitor Agent
* [ ] Package as a **background service (daemon)** for Linux

---

## 📖 Project Goal

The end goal is to create an AI assistant that:

* Runs as a **background service** in Linux
* Listens for **voice or text commands**
* Executes **system-level actions safely**
* Provides **natural feedback** to the user
* Learns **user preferences** and makes **proactive decisions**

---

## 🛠️ Current Status

This is **Version 0** (prototype).

* Works in **text mode** and **basic voice mode**
* Can check disk, memory, respond with greetings, and verify installations
* Confirmation is **terminal-based only**

---

## 👨‍💻 Author

* **Gopu Girish, Shamir Ashraf, Yadhu Krishnan PU** (Final Year BTech Project)
* Project Repository: [GitHub](https://github.com/shamiroxs/AIP)

