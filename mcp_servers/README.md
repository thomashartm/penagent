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

## Performance Notes

- **Memory Usage**: All services typically use 1-2GB RAM total
- **Startup Time**: Initial build takes 5-10 minutes, subsequent starts take 1-2 minutes
- **Network**: Services communicate via internal Docker network `mcp_servers_mcp-network`

## Security Notes

- ZAP daemon runs with API key disabled for development
- All MCP servers run in isolated containers
- No persistent data is stored in containers (use volumes if needed)
- Services are not exposed to external networks by default 