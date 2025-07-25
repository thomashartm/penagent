# Pentest-Agent: Autonomous Pentesting AI Agent

> **⚠️ Work in Progress:** This project is under active development and is not yet production-ready. Features, APIs, and behaviors may change frequently.

## Overview
Pentest-Agent is an autonomous pentesting AI agent built with Python and the langgraph framework, inspired by Agent_PenX. It orchestrates multiple tools (shell, Python REPL, web browsing, RAG, web search) to achieve high-level security goals, logs every step, and generates professional Markdown reports.

---

## 1. Setup

### Prerequisites
- Python 3.9+
- [Poetry](https://python-poetry.org/docs/#installation)
- [Ollama](https://ollama.com/download) (for local LLM backend)
- [Docker](https://docs.docker.com/get-docker/) (for KaliContainerTool)

### Clone the Repository
```sh
git clone <repo-url>
cd cognizant-vibe
```

### Install Dependencies (Poetry Only)
This project is designed to be used with [Poetry](https://python-poetry.org/). Other install methods are not supported.
```sh
poetry install
```

### Activate the Virtual Environment
```sh
poetry shell
```

### Ollama Setup
- Download and install Ollama from [Ollama.com](https://ollama.com/download)
- Pull a model (e.g., `llama3`):
  ```sh
  ollama pull llama3
  ollama serve &
  ```
- Ensure Ollama is running at `http://localhost:11434`

---

### Kali Linux Docker Container Setup (for KaliContainerTool)

1. **Install Docker** ([instructions](https://docs.docker.com/get-docker/))
2. **Pull and run a Kali container named `kali`:**
   ```sh
   docker run -d --name kali -it kalilinux/kali-rolling tail -f /dev/null
   ```
3. **Install Metasploit and other tools inside the container:**
   ```sh
   docker exec -it kali bash
   # Inside the container:
   apt update && apt install -y metasploit-framework gobuster hydra nmap
   exit
   ```
4. **Verify the container is running:**
   ```sh
   docker ps
   # Should show a container named 'kali'
   ```
5. **(Optional) Install more tools as needed:**
   ```sh
   docker exec -it kali apt install -y <toolname>
   ```

---

## 2. Usage

All CLI commands use the Poetry virtual environment. Use `poetry run pentest-agent ...` for all invocations.

### Run a Pentest Task
```sh
poetry run pentest-agent run --task "Scan https://public-firing-range.appspot.com/ for Reflected XSS"
```

### List Available Tools
```sh
poetry run pentest-agent tools list
```

### Generate a Markdown Report
```sh
poetry run pentest-agent report --input process_logs.json --output report.md
```

---

## 3. Testing

### Run Unit Tests
```sh
poetry run pytest
```

### Linting and Code Style
```sh
poetry run flake8 src/
```

---

## Project Structure
- `src/` — All source code
- `.gitignore` — Excludes venv, cache, logs, build artifacts
- `pyproject.toml` — Poetry dependency management
- `requirements.txt` — pip compatibility (for reference only)
- `README.md` — This file

---

## License
MIT
