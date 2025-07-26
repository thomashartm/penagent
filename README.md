# Pentest-Agent: Autonomous Pentesting AI Agent

> **⚠️ Work in Progress:** This project is under active development and is not yet production-ready. Features, APIs, and behaviors may change frequently.

## Overview
Pentest-Agent is an autonomous pentesting AI agent built with Python and the langgraph framework, inspired by Agent_PenX. It orchestrates multiple tools (shell, Python REPL, web browsing, RAG, web search) to achieve high-level security goals, logs every step, and generates professional Markdown reports.

---

## Frontend (Streamlit Web UI)

A modern web-based frontend is available using [Streamlit](https://streamlit.io/).

### How to Run the Frontend

1. **Install dependencies**
   - If using Poetry:
     ```sh
     poetry install
     ```
   - Or with pip:
     ```sh
     pip install -r requirements.txt
     ```

2. **Start the Streamlit app**
   - If using Poetry (recommended):
     ```sh
     poetry run streamlit run src/frontend/app.py
     ```
   - If using a virtual environment:
     ```sh
     source .venv/bin/activate
     streamlit run src/frontend/app.py
     ```

3. **Open your browser**
   - The app will open automatically, or visit [http://localhost:8501](http://localhost:8501)

4. **Using the UI**
   - Enter your pentest goal or select a prompt card, then click **Send**.
   - The right panel streams the agent’s Thought → Action → Observation cycles live.
   - The bottom panel shows discovered vulnerabilities/findings in a table.
   - The top toolbar shows tool/container status and prompt history.

---

## 1. Setup

### Prerequisites
- Python 3.9+
- [Poetry](https://python-poetry.org/docs/#installation)
- [Ollama](https://ollama.com/download) (for local LLM backend)
- [Docker](https://docs.docker.com/get-docker/) (for containerized tools)

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

### Containerized Pentest Environment (Docker Compose)

This project provides a full pentest environment using Docker Compose, including:
- **Kali Linux** (with common tools pre-installed)
- **Playwright** (for browser automation)
- **OWASP ZAP** (for web app security scanning)

#### Start All Services
```sh
cd containers
# Build and start all containers in the background
docker-compose up --build -d
```

#### Verify Services
- **Kali**: Should be running as `kali` (with tools like metasploit, gobuster, hydra, nmap, etc.)
- **Playwright**: Ready for browser-based automation
- **ZAP**: Accessible at [http://localhost:8090](http://localhost:8090)

Check running containers:
```sh
docker ps
```

#### (Optional) Add More Tools to Kali
Edit `containers/kali.Dockerfile` and rebuild:
```sh
docker-compose build kali
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
