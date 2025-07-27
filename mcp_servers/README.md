# MCP Servers - Pentest-Agent Containerized Environment

This directory contains the Docker Compose orchestration for all MCP (Model Context Protocol) servers used by the Pentest-Agent.

## Architecture Overview

The MCP server environment consists of:

- **Kali MCP Server** (Port 8001): Shell command execution in Kali Linux
- **WebSearch MCP Server** (Port 8002): Web search functionality via DuckDuckGo
- **Discovery MCP Server** (Port 8003): Lightweight web app discovery/spidering
- **RAG MCP Server** (Port 8004): Knowledge base operations
- **ZAP MCP Server** (Port 8005): OWASP ZAP web app scanning orchestration
- **ZAP Daemon** (Port 8090): OWASP ZAP daemon (internal use only)
- **Playwright** (No port): Browser automation support

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available for all containers

### Build and Start All Services
```bash
# Build all containers and start in detached mode
docker-compose up --build -d
```

### Verify Services Are Running
```bash
# Check container status
docker-compose ps

# Check logs for all services
docker-compose logs

# Check logs for specific service
docker-compose logs kali
docker-compose logs zap-mcp
```

### Stop All Services
```bash
# Stop and remove containers, networks, and volumes
docker-compose down -v --remove-orphans
```

## Service Management

### Start Specific Services
```bash
# Start only Kali and WebSearch
docker-compose up -d kali websearch

# Start ZAP and its MCP server
docker-compose up -d zap zap-mcp
```

### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart kali
```

### View Real-time Logs
```bash
# Follow logs for all services
docker-compose logs -f

# Follow logs for specific service
docker-compose logs -f zap-mcp
```

## Troubleshooting

### Common Issues

#### 1. Network "mcp_servers_mcp-network" Resource is still in use
**Problem**: Docker network cannot be removed because containers are still attached.

**Solution**:
```bash
# Force remove all containers and networks
docker-compose down -v --remove-orphans

# If that doesn't work, manually remove the network
docker network ls
docker network rm mcp_servers_mcp-network
```

#### 2. Port Already in Use
**Problem**: Port 8001-8005 or 8090 is already occupied.

**Solution**:
```bash
# Check what's using the port
lsof -i :8001
lsof -i :8002
# etc.

# Stop conflicting services or modify ports in docker-compose.yml
```

#### 3. Container Build Failures
**Problem**: Docker build fails due to missing dependencies or network issues.

**Solution**:
```bash
# Clean build (no cache)
docker-compose build --no-cache

# Build specific service
docker-compose build --no-cache kali
```

#### 4. ZAP Daemon Not Starting
**Problem**: ZAP container exits immediately or health check fails.

**Solution**:
```bash
# Check ZAP logs
docker-compose logs zap

# Check if ZAP API is responding
curl http://localhost:8090/JSON/core/view/version/

# Restart ZAP with fresh state
docker-compose down zap zap-mcp
docker-compose up -d zap zap-mcp
```

#### 5. MCP Server Connection Issues
**Problem**: Agent cannot connect to MCP servers.

**Solution**:
```bash
# Test MCP server endpoints
curl -X POST http://localhost:8001/run -H "Content-Type: application/json" -d '{"command":"echo hello"}'
curl -X POST http://localhost:8002/run -H "Content-Type: application/json" -d '{"command":"test search"}'

# Check if containers are running
docker-compose ps

# Check network connectivity
docker network inspect mcp_servers_mcp-network
```

### Clean Slate Reset
If you encounter persistent issues, perform a complete reset:

```bash
# Stop and remove everything
docker-compose down -v --remove-orphans

# Remove all stopped containers
docker container prune -f

# Remove unused networks
docker network prune -f

# Remove unused images (optional)
docker image prune -f

# Rebuild and start fresh
docker-compose up --build -d
```

## Service Endpoints

### MCP Server Endpoints
All MCP servers accept POST requests to `/run` with JSON payload:
```json
{
  "command": "your command here"
}
```

| Service | Port | Endpoint | Purpose |
|---------|------|----------|---------|
| Kali | 8001 | `http://localhost:8001/run` | Shell command execution |
| WebSearch | 8002 | `http://localhost:8002/run` | Web search functionality |
| Discovery | 8003 | `http://localhost:8003/run` | Web app discovery/spidering |
| RAG | 8004 | `http://localhost:8004/run` | Knowledge base operations |
| ZAP MCP | 8005 | `http://localhost:8005/run` | ZAP scanning orchestration |

### ZAP Daemon (Internal)
- **API**: `http://localhost:8090`
- **Web UI**: `http://localhost:8090/zap/`
- **Note**: Only accessible through ZAP MCP server

## Development

### Adding New MCP Servers
1. Create a new directory in `src/` for your server
2. Create a FastAPI server with `/run` endpoint
3. Create a Dockerfile for the server
4. Add service to `docker-compose.yml`
5. Update agent's MCP client configuration

### Modifying Existing Servers
1. Edit the Python server code in `src/[service]/`
2. Rebuild the specific service:
   ```bash
   docker-compose build [service-name]
   docker-compose up -d [service-name]
   ```

### Debugging
```bash
# Run service in foreground for debugging
docker-compose up [service-name]

# Execute commands in running container
docker-compose exec kali bash
docker-compose exec zap-mcp sh
```

## MCP CLI Usage and Examples

The `mcp_cli.py` tool provides a comprehensive command-line interface for testing and debugging all MCP servers. It uses the FastMCP client API and is designed for manual testing, debugging, and exploration of MCP server capabilities.

### Features
- Container status checking
- Server connection management
- Tool discovery
- Tool testing (send test payloads)
- Interactive mode
- Quick one-liner testing

### Quick Start

1. **Start the MCP Servers**
   ```bash
   docker-compose up -d
   ```
2. **Check Container Status**
   ```bash
   python mcp_cli.py --check-containers
   ```
3. **List Available Servers**
   ```bash
   python mcp_cli.py --list-servers
   ```
4. **Start Interactive Mode**
   ```bash
   python mcp_cli.py --interactive
   ```

### Usage Examples

#### Interactive Mode (Recommended)
```bash
python mcp_cli.py -i
```
In interactive mode, you can:
```
mcp> connect kali
mcp[kali]> list
mcp[kali]> call nmap {"target": "127.0.0.1", "options": "-sV"}
mcp[kali]> disconnect
mcp> connect websearch
mcp[websearch]> call search {"query": "python programming", "max_results": 3}
```

#### Quick Testing Commands

- **Kali**
  ```bash
  python mcp_cli.py -s kali
  python mcp_cli.py -s kali -t nmap -a '{"target": "127.0.0.1", "options": "-sV"}'
  python mcp_cli.py -s kali -t gobuster -a '{"url": "https://example.com", "wordlist": "/usr/share/wordlists/dirb/common.txt"}'
  ```
- **ZAP**
  ```bash
  python mcp_cli.py -s zap
  python mcp_cli.py -s zap -t spider -a '{"url": "https://example.com"}'
  python mcp_cli.py -s zap -t alerts -a '{"risk_level": "High"}'
  ```
- **WebSearch**
  ```bash
  python mcp_cli.py -s websearch
  python mcp_cli.py -s websearch -t search -a '{"query": "artificial intelligence", "max_results": 5}'
  python mcp_cli.py -s websearch -t search_news -a '{"query": "cybersecurity", "max_results": 3}'
  ```
- **RAG**
  ```bash
  python mcp_cli.py -s rag
  python mcp_cli.py -s rag -t search -a '{"query": "nmap", "max_results": 3}'
  python mcp_cli.py -s rag -t store -a '{"category": "test", "content": "This is test content"}'
  ```
- **Discovery (OWASP)**
  ```bash
  python mcp_cli.py -s discovery
  python mcp_cli.py -s discovery -t spider -a '{"url": "https://example.com", "max_urls": 5}'
  python mcp_cli.py -s discovery -t check_headers -a '{"url": "https://example.com"}'
  ```

#### Interactive Mode Commands
| Command | Description | Example |
|---------|-------------|---------|
| `connect <server>` | Connect to a specific server | `connect kali` |
| `disconnect` | Disconnect from current server | `disconnect` |
| `list` | List available tools | `list` |
| `call <tool> <args>` | Call a tool with JSON arguments | `call nmap {"target": "127.0.0.1"}` |
| `quit` / `exit` / `q` | Exit interactive mode | `quit` |

#### Command Line Options
| Option | Short | Description |
|--------|-------|-------------|
| `--server` | `-s` | Target server for operations |
| `--tool` | `-t` | Tool name to call |
| `--args` | `-a` | JSON arguments for tool call |
| `--interactive` | `-i` | Start interactive mode |
| `--list-servers` | `-l` | List available servers |
| `--check-containers` | `-c` | Check container status |

#### Troubleshooting
- **Missing containers**: `docker-compose up -d`
- **Failed to connect**: Check containers with `docker ps | grep mcp-` and restart if needed
- **Invalid JSON arguments**: Use single quotes and valid JSON
- **Tool not found**: Use `list` to see available tools and check spelling

---

### Common Error: `ModuleNotFoundError: No module named 'fastmcp'`

If you see this error when running `mcp_cli.py`:

```
Traceback (most recent call last):
  File ".../mcp_cli.py", line 12, in <module>
    from fastmcp import Client
ModuleNotFoundError: No module named 'fastmcp'
```

**How to Fix:**

**1. If you are using Poetry (recommended):**
Run the CLI using Poetry, which uses the correct virtual environment:
```bash
poetry run python mcp_cli.py --list-servers
```

**2. If you want to run it with plain Python:**
Install `fastmcp` in your current Python environment:
```bash
pip install fastmcp
```
Or, for Python 3.12 specifically:
```bash
python3.12 -m pip install fastmcp
```

**3. If you are using a virtual environment:**
Activate the environment before running the script:
```bash
source .venv/bin/activate
python mcp_cli.py --list-servers
```

If you still have issues, double-check your environment and how you are running the script.

## Performance Notes

- **Memory Usage**: All services typically use 1-2GB RAM total
- **Startup Time**: Initial build takes 5-10 minutes, subsequent starts take 1-2 minutes
- **Network**: Services communicate via internal Docker network `mcp_servers_mcp-network`

## Security Notes

- ZAP daemon runs with API key disabled for development
- All MCP servers run in isolated containers
- No persistent data is stored in containers (use volumes if needed)
- Services are not exposed to external networks by default 