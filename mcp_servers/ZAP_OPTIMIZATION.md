# ZAP Container Optimization

## Problem
The current ZAP setup uses **two separate containers**:
1. `pentest-zap` - Official ZAP daemon (port 8090)
2. `mcp-zap` - MCP server wrapper (port 8005)

This is inefficient compared to the Kali setup, which uses a single container.

## Solution: Combined ZAP Container

### Benefits of Single Container Approach

1. **Resource Efficiency**
   - Fewer containers to manage
   - Reduced memory overhead
   - Faster startup time

2. **Simplified Architecture**
   - No inter-container networking needed
   - Direct localhost communication
   - Easier debugging and monitoring

3. **Consistency**
   - Matches the Kali container pattern
   - Unified container management
   - Simpler docker-compose configuration

### Implementation

#### Files Created:
- `zap_combined.Dockerfile` - Single container with both ZAP daemon and MCP server
- `zap_server_combined.py` - MCP server optimized for same-container deployment
- `docker-compose-optimized.yml` - Optimized docker-compose configuration

#### Key Changes:
1. **Base Image**: Uses official ZAP image as base
2. **Python Installation**: Adds Python and FastAPI to ZAP container
3. **Startup Script**: Runs both ZAP daemon and MCP server
4. **Local Communication**: MCP server uses `localhost:8090` instead of container networking

### Usage

#### Current Setup (Two Containers):
```bash
cd mcp_servers
docker-compose up -d zap zap-mcp
```

#### Optimized Setup (Single Container):
```bash
cd mcp_servers
docker-compose -f docker-compose-optimized.yml up -d zap
```

### Comparison

| Aspect | Current (2 containers) | Optimized (1 container) |
|--------|----------------------|-------------------------|
| Containers | 2 | 1 |
| Memory Usage | Higher | Lower |
| Startup Time | Slower | Faster |
| Network Complexity | Inter-container | Localhost |
| Debugging | More complex | Simpler |
| Consistency | Different from Kali | Matches Kali pattern |

### Migration Path

1. **Test the optimized version**:
   ```bash
   cd mcp_servers
   docker-compose -f docker-compose-optimized.yml up -d zap
   ```

2. **Verify functionality**:
   ```bash
   curl -X POST http://localhost:8005/run \
     -H "Content-Type: application/json" \
     -d '{"command": "alerts"}'
   ```

3. **Replace current setup** (if testing successful):
   - Replace `docker-compose.yml` with optimized version
   - Update documentation
   - Remove old ZAP containers

### Why This Approach is Better

1. **Follows Established Pattern**: Matches how Kali container works
2. **Reduces Complexity**: Eliminates unnecessary container separation
3. **Improves Performance**: Faster startup and lower resource usage
4. **Easier Maintenance**: Single container to manage and debug
5. **Better Consistency**: All MCP servers follow similar patterns

The current two-container approach likely exists because ZAP is designed as an API-first tool, but for our use case, the single-container approach is more efficient and consistent with the rest of the architecture. 