# Pentest-Agent: Autonomous Pentesting AI Agent

> **⚠️ Work in Progress:** This project is under active development and is not yet production-ready. Features, APIs, and behaviors may change frequently.

## Overview
Pentest-Agent is an autonomous pentesting AI agent built with Python and the langgraph framework, inspired by Agent_PenX. It uses a graph-based, stateful workflow driven by LangGraph and instrumented via MCP (Model Context Protocol) servers. The agent orchestrates multiple tools (Kali Linux, web search, OWASP ZAP, RAG) to achieve high-level security goals, logs every step, and generates professional Markdown reports.

---

## Architecture

### MCP Server Layer
Each pentest tool runs as a standalone FastAPI-based MCP server:
- **Kali MCP Server** (Port 8001): Executes shell commands in Kali Linux container
- **WebSearch MCP Server** (Port 8002): Performs web searches using DuckDuckGo
- **OWASP MCP Server** (Port 8003): Web application security testing and spidering
- **RAG MCP Server** (Port 8004): Knowledge base operations with pentest methodologies
- **ZAP MCP Server** (Port 8005): Interfaces with OWASP ZAP daemon for web app scanning

### LangGraph Workflow
The agent uses LangGraph to define and execute stateful workflows as directed graphs:
- **LLM Node**: Wraps Ollama calls for reasoning
- **MCP Client Node**: Makes HTTP calls to MCP tool servers
- **Planner Node**: Breaks high-level tasks into graph sub-tasks
- **Logger Node**: Writes thought/action/observation state to outputs

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
   - The right panel streams the agent's Thought → Action → Observation cycles live.
   - The bottom panel shows discovered vulnerabilities/findings in a table.
   - The top toolbar shows tool/container status and prompt history.

---

## 1. Setup

### Prerequisites
- Python 3.9+
- [Poetry](https://python-poetry.org/docs/#installation)
- [Ollama](https://ollama.com/download) (for local LLM backend)
- [Docker](https://docs.docker.com/get-docker/) (for containerized MCP servers)

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

### MCP Server Environment (Docker Compose)

This project provides a full pentest environment using Docker Compose with MCP servers:

#### Start All MCP Servers (Detached Mode)
```sh
cd mcp_servers
# Build and start all containers in detached mode (background)
docker-compose up --build -d
```

#### MCP Server Endpoints
- **Kali MCP**: `http://localhost:8001` - Shell command execution
- **WebSearch MCP**: `http://localhost:8002` - Web search functionality
- **OWASP MCP**: `http://localhost:8003` - Web app security testing
- **RAG MCP**: `http://localhost:8004` - Knowledge base operations
- **ZAP MCP**: `http://localhost:8005` - OWASP ZAP web app scanning
- **ZAP Daemon**: `http://localhost:8090` - ZAP API/UI (internal use only)

#### Verify Services
Check running containers:
```sh
docker-compose ps
```

Check MCP server logs:
```sh
docker-compose logs [service-name]
# Example: docker-compose logs zap-mcp
```

#### Stop Services
```sh
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 2. Usage

All CLI commands use the Poetry virtual environment. Use `poetry run pentest-agent ...` for all invocations.

### Run a Pentest Task
```sh
poetry run pentest-agent run --command "Scan https://public-firing-range.appspot.com/ for Reflected XSS"
```

### Example Commands
```sh
# Network reconnaissance
poetry run pentest-agent run --command "Perform network reconnaissance on target.com"

# Web application testing
poetry run pentest-agent run --command "Test https://example.com for OWASP Top 10 vulnerabilities"

# Information gathering
poetry run pentest-agent run --command "Gather information about target organization"
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
```
cognizant-vibe/
├── src/
│   ├── agent/
│   │   ├── graph_client.py          # Main GraphClient class
│   │   ├── langgraph_workflow.py    # LangGraph workflow definition
│   │   └── nodes/                   # Workflow nodes
│   ├── frontend/                    # Streamlit web UI
│   └── mcp_servers/                 # MCP server code (legacy)
├── mcp_servers/
│   ├── docker-compose.yml           # MCP server orchestration
│   ├── *.Dockerfile                 # Container definitions
│   └── src/
│       ├── kali/                    # Kali MCP server
│       ├── websearch/               # WebSearch MCP server
│       ├── owasp/                   # OWASP MCP server
│       ├── rag/                     # RAG MCP server
│       └── zap/                     # ZAP MCP server
├── outputs/                         # Job outputs and logs
├── pyproject.toml                   # Poetry configuration
└── README.md                        # This file
```

---

## License
MIT
