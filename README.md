# 🎙️ Leo (Version 3)

**Leo** is our Linux-based **voice + text desktop assistant**, evolved from Version 2 with **LLM-based intelligence**, stronger **safety**, and **command verification layers** powered entirely **offline** (local models only — no cloud).

---

## 🚀 What’s New in Version 3

### 🧠 Local LLM Intelligence (Offline)

* Natural conversation fallback for unknown commands
* Context-aware responses using recent memory
* Can **suggest structured commands**, but **never executes them directly**
* Configurable to support **Ollama** or local model servers

### 🔐 Safety-First Execution Flow

* Zero blind execution from AI
* **Multiple safety checkpoints**:

  * Regex intent → direct deterministic actions ✔️
  * LLM proposals → **SafetyAgent → User Confirmation → Execution**
  * Command validation using Markov-based anomaly detection
* Full logging of LLM outputs & safety decisions

### 🧩 Modular NL Routing Architecture

A new **NL Router** intelligently decides if the LLM should:

* Provide a conversational answer
* Suggest a grounded system action
* Ask clarifying questions if uncertain

### 📜 Configurable & Auditable

* LLM configuration now externalized (model path, ports, parameters)
* Dedicated LLM logs for transparency: `~/.leo/llm.log`

---

## 🏗️ Updated Internal Architecture

| Module/Feature           | Status   | Description                                       |
| ------------------------ | -------- | ------------------------------------------------- |
| Regex Intent Recognition | Improved | Unknown → fallback to LLM router                  |
| Coordinator              | Improved | Routes control flow based on intent type          |
| Action Execution         | Hardened | Requires confirmation for LLM-sourced actions     |
| Context Memory           | New      | Short-term recall (previous queries/system state) |
| LLM Agent                | New      | Talks to local model (Ollama) with safe prompts   |
| NL Router                | New      | Decides reply vs command suggestion               |
| LLM Safety Layer         | New      | Validates suggestions + blocks unsafe tokens      |
| Markov Verifier          | New      | Detects hallucinated command sequences            |
| Logging System           | Expanded | Adds LLM + safety logs for auditing               |
| Config System            | New      | `llm_config.yaml` for model + thresholds          |

All new code remains **local-only**.
**No internet calls** by the assistant or the LLM.

---

## 📂 New Files in V3

| File                                               | Purpose                              |
| -------------------------------------------------- | ------------------------------------ |
| `assistant/agents/llm_agent.py`                    | Local LLM interface                  |
| `assistant/agents/nl_router.py`                    | Natural language routing logic       |
| `assistant/data/prompts.py`                        | System prompts for grounded behavior |
| `assistant/agents/context_memory.py`               | Limited context storage              |
| `assistant/security/llm_safety.py`                 | Command risk analysis                |
| `assistant/utils/response_formatter.py`            | TTS/UI-friendly response formatting  |
| `assistant/agents/verification_markov.py`          | Markov safety model                  |
| `assistant/tests/test_llm_integration.py`          | Automated verification               |
| `assistant/agents/langchain_wrapper.py` (optional) | Tool-augmented reasoning             |
| `assistant/config/llm_config.yaml`                 | Local model settings                 |
| `systemd/leo-llm.service` (optional)               | Optional local LLM auto-start        |

---

## 📦 Requirements

Everything from V2 **plus:**

* Local LLM runtime (example: **Ollama**)
* At least **6GB RAM** recommended for smooth model use

---

## 🧰 Usage (V3 Flow)

### Deterministic Commands (Regex)

```bash
python -m assistant.main --text "leo open firefox"
```

Direct execution → Safety → Done.

### Natural Conversation (LLM Fallback)

```bash
python -m assistant.main --text "what is python venv?"
```

LLM responds conversationally.
No execution happens.

### LLM Suggested Commands

```bash
python -m assistant.main --text "install curl"
```

Flow:

1. LLM proposes: `sudo apt install curl`
2. Safety check → logs
3. Leo asks confirmation:

   > Should I install curl? (yes/no)
4. Only then executes

---

## 🛡️ Safety Guarantees

| Risk                                  | Mitigation                               |
| ------------------------------------- | ---------------------------------------- |
| LLM tries to run destructive commands | Hard block list + Markov anomaly scoring |
| LLM tries to execute directly         | No executor access — only proposals      |
| Hidden shell injection                | Sanitization before user confirmation    |
| Untraceable actions                   | Full audit logging                       |

👑 **User is always the final checkpoint.**

---

## 🧪 Testing Checklist

| Test                  | How                                            |
| --------------------- | ---------------------------------------------- |
| Regex commands        | Run GUI actions like “open browser”            |
| Fallback conversation | Ask general questions                          |
| Safety intervention   | Try malicious text like: “delete system files” |
| Confirmation required | Installation requests                          |
| Logging               | Check `~/.leo/llm.log`                         |

---

## ⚠️ Known Limitations

* Still requires **X11** for GUI control
* Local models vary in accuracy for command suggestion
* Context memory resets on restart (configurable)

---

## 👨‍💻 Contributors

* **Gopu Girish, Shamir Ashraf, Yadhu Krishnan PU**
* GitHub: [`shamiroxs/AIP`](https://github.com/shamiroxs/AIP)

---

## 👍 Team Notes for Demo

✔️ Use **text mode** for testing LLM flows
✔️ Confirm **Ollama/local LLM server** is running
✔️ Always check GUI automation in **X11 session**
