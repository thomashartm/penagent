# Security Testing Orchestration Platform

A comprehensive security testing orchestration platform using LangGraph, MCP (Model Context Protocol) servers, and local LLM integration.

## Quick Start

### 1. Service Management

Use the provided service management script to start all required services:

```bash
# Start all services (Ollama + MCP containers)
./start_services.sh start

# Check service status
./start_services.sh status

# View container logs
./start_services.sh logs containers

# Stop all services
./start_services.sh stop

# Clean up everything
./start_services.sh clean
```

### 2. Install Dependencies

```bash
# Install core project dependencies
cd core
poetry install
```

### 3. Run Security Scans

```bash
# Run a security scan
poetry run python -m core.cli scan example.com --verbose

# Chat with the AI
poetry run python -m core.cli chat "Hello, how can you help me with security testing?"
```

## Architecture

The project consists of two main components:

### MCP Servers (`mcp_servers/`)
- **Kali Server**: Pentesting tools (nmap, gobuster, hydra, nikto, metasploit, etc.)
- **WebSearch Server**: Web search and news aggregation
- **RAG Server**: Knowledge base and document storage

### Core Orchestration (`core/`)
- **LangGraph Workflow**: Orchestrates security testing phases
- **LLM Integration**: Uses local Ollama models
- **MCP Client**: Connects to MCP servers for tool execution

## Service Management

The `start_services.sh` script provides comprehensive service management:

- **Health Checks**: Verifies Ollama and Docker container status
- **Automatic Startup**: Starts services in the correct order
- **Logging**: View logs for troubleshooting
- **Cleanup**: Complete teardown of all services

### Available Commands

| Command | Description |
|---------|-------------|
| `start` | Start all services (Ollama + MCP containers) |
| `stop` | Stop all services |
| `restart` | Restart all services |
| `status` | Check status of all services |
| `logs [service]` | Show logs (service: ollama\|containers) |
| `clean` | Stop all services and clean up |

### Service Requirements

- **Ollama**: Local LLM server (port 11434)
- **Docker**: Container runtime
- **MCP Containers**: kali, websearch, rag

## Development

### Prerequisites

- Python 3.12+
- Poetry
- Docker & Docker Compose
- Ollama

### Setup

1. **Install Ollama**: https://ollama.ai/
2. **Start Services**: `./start_services.sh start`
3. **Install Dependencies**: `cd core && poetry install`
4. **Run Tests**: `cd mcp_servers && python tests/run_all_tests.py`

### Testing

```bash
# Test MCP servers
cd mcp_servers
python tests/run_all_tests.py

# Test core orchestration
cd core
poetry run python test_basic.py
```

## Troubleshooting

### Common Issues

1. **Ollama not running**: Run `ollama serve` or use `./start_services.sh start`
2. **Containers not starting**: Check Docker and run `./start_services.sh logs containers`
3. **MCP connection errors**: Ensure containers are running and healthy

### Service Status

Check service status anytime:
```bash
./start_services.sh status
```

This will show the status of:
- Ollama server
- Docker daemon
- MCP containers (kali, websearch, rag)

## Conversation CLI Examples

You can start an interactive chat session with the orchestration system using the provided script:

```bash
./start_conversation.sh
```

Example session:
```
Security Orchestration Chat CLI
Type your message and press Enter. Type 'exit' or 'quit' to leave.
You > Hello, what can you do?
[AI Response...]
You > Scan example.com for vulnerabilities
[AI Response...]
You > exit
Goodbye!
```

- The script will check that all required services are running and start them if needed.
- Each message is sent to the core CLI chat command.
- Type `exit` or `quit` to leave the session.

## License

MIT License - see LICENSE file for details.
