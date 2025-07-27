# Container Naming Convention

## Overview
All containers in this project follow a consistent naming convention to make them easily identifiable and maintainable.

## Naming Rules

### MCP Servers
All MCP (Model Context Protocol) servers use the `mcp-` prefix:

- `mcp-kali` - Kali Linux MCP server (port 8001)
- `mcp-websearch` - Web search MCP server (port 8002)
- `mcp-discovery` - Web app discovery MCP server (port 8003)
- `mcp-rag` - RAG knowledge base MCP server (port 8004)
- `mcp-zap` - ZAP daemon + MCP server (ports 8005, 8090)

### Non-MCP Services
Non-MCP services use descriptive prefixes:

- `pentest-playwright` - Playwright browser automation (not MCP)

## Benefits

1. **Easy Identification**: All MCP servers are clearly identifiable with the `mcp-` prefix
2. **Consistent Pattern**: Makes it easy to find and manage related containers
3. **Clear Purpose**: Container names immediately indicate their function
4. **Simplified Management**: Easy to filter and manage containers by type

## Usage Examples

### List all MCP servers:
```bash
docker ps --filter "name=mcp-"
```

### List all containers:
```bash
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"
```

### Check specific MCP server status:
```bash
docker ps | grep mcp-kali
docker ps | grep mcp-zap
```

## Port Mapping

| Container | Port | Purpose |
|-----------|------|---------|
| mcp-kali | 8001 | Kali Linux MCP server |
| mcp-websearch | 8002 | Web search MCP server |
| mcp-discovery | 8003 | Web app discovery MCP server |
| mcp-rag | 8004 | RAG knowledge base MCP server |
| mcp-zap | 8005 | ZAP MCP server |
| mcp-zap | 8090 | ZAP API/UI (internal) |

## Code References

The naming convention is reflected in the codebase:

- `src/tools/kali_container_tool.py` - Uses `mcp-kali` as default container name
- `src/frontend/app.py` - Checks for `mcp-kali` and `mcp-zap` containers
- `src/agent/nodes/mcp_client_node.py` - Maps service names to MCP endpoints

## Migration Notes

This naming convention was implemented to replace the previous inconsistent naming:
- `kali` → `mcp-kali`
- `pentest-zap-combined` → `mcp-zap`
- Other MCP servers already had the `mcp-` prefix 