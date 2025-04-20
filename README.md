# 🧠 LLM Intent Assistant – Setup Guide

This guide will help you get the project running on your machine. It includes Python setup, CLI tooling, and environment configuration.

---

## ✅ Prerequisites

Make sure you have the following tools installed:

- Python 3.10+
- [ollama](https://ollama.com) (for local LLM models)
- [bat](https://github.com/sharkdp/bat) (optional but useful for viewing files)
- Shell: `zsh` (this guide assumes you're using zsh)

---

## ⚙️ Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone <repo-url>
cd gigi
```

### 2. Install Python Dependencies

Use `venv`, `poetry`, or `pip` as you prefer. If using `pip`:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🛠️ Configure CLI Access (for `mg` or similar tools)

If you're using a tool installed to `~/.local/bin`, ensure it's in your `$PATH`.

### Edit your `.zshrc`:

```bash
nano ~/.zshrc
```

And add:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload your shell config:

```bash
source ~/.zshrc
```

Confirm it works:

```bash
which mg
```

---

## 🧪 Running the App

From the project root:

```bash
cd src/app
python main.py
```

---

## ✅ Running Tests

From the `src/` folder:

```bash
cd src
python -m unittest discover -s tests -v
```

---

## 🤖 Using Ollama

Ensure `ollama` is installed and running, then pull and run the model:

```bash
ollama run llama3.2
```

If `ollama` is not found:

1. [Download and install Ollama](https://ollama.com/download)
2. Restart your terminal.

---

## 🧯 Tips & Troubleshooting

- Use `bat` to read files with syntax highlighting:
  ```bash
  bat README.md
  ```
- Make sure `mg` or any custom CLI tools are executable:
  ```bash
  chmod +x ~/.local/bin/mg
  ```