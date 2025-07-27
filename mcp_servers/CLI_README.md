# MCP Servers CLI - Manual Testing and Debugging Tool

A comprehensive command-line interface for testing and debugging all MCP servers in the project. This CLI uses the FastMCP client API and is designed for manual testing, debugging, and exploration of MCP server capabilities.

## Features

- 🔍 **Container Status Checking** - Verify all MCP containers are running
- 🔌 **Server Connection Management** - Connect/disconnect to any MCP server
- 📋 **Tool Discovery** - List all available tools from each server
- 🧪 **Tool Testing** - Send test payloads to any tool with custom arguments
- 🎯 **Interactive Mode** - Real-time testing with command prompt
- ⚡ **Quick Testing** - One-liner commands for rapid testing

## Prerequisites

1. **Docker containers running**: All MCP servers must be started
2. **FastMCP installed**: The CLI requires the FastMCP library
3. **Python 3.12+**: Required for FastMCP compatibility

## Quick Start

### 1. Start the MCP Servers
```bash
docker-compose up -d
```

### 2. Check Container Status
```bash
python mcp_cli.py --check-containers
```

### 3. List Available Servers
```bash
python mcp_cli.py --list-servers
```

### 4. Start Interactive Mode
```bash
python mcp_cli.py --interactive
```

## Usage Examples

### Interactive Mode (Recommended)
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

### Quick Testing Commands

#### Test Kali Server
```bash
# List all tools
python mcp_cli.py -s kali

# Test nmap tool
python mcp_cli.py -s kali -t nmap -a '{"target": "127.0.0.1", "options": "-sV"}'

# Test gobuster tool
python mcp_cli.py -s kali -t gobuster -a '{"url": "https://example.com", "wordlist": "/usr/share/wordlists/dirb/common.txt"}'
```

#### Test ZAP Server
```bash
# List all tools
python mcp_cli.py -s zap

# Test spider tool
python mcp_cli.py -s zap -t spider -a '{"url": "https://example.com"}'

# Test alerts tool
python mcp_cli.py -s zap -t alerts -a '{"risk_level": "High"}'
```

#### Test WebSearch Server
```bash
# List all tools
python mcp_cli.py -s websearch

# Test search tool
python mcp_cli.py -s websearch -t search -a '{"query": "artificial intelligence", "max_results": 5}'

# Test search_news tool
python mcp_cli.py -s websearch -t search_news -a '{"query": "cybersecurity", "max_results": 3}'
```

#### Test RAG Server
```bash
# List all tools
python mcp_cli.py -s rag

# Test search tool
python mcp_cli.py -s rag -t search -a '{"query": "nmap", "max_results": 3}'

# Test store tool
python mcp_cli.py -s rag -t store -a '{"category": "test", "content": "This is test content"}'
```

#### Test Discovery (OWASP) Server
```bash
# List all tools
python mcp_cli.py -s discovery

# Test spider tool
python mcp_cli.py -s discovery -t spider -a '{"url": "https://example.com", "max_urls": 5}'

# Test check_headers tool
python mcp_cli.py -s discovery -t check_headers -a '{"url": "https://example.com"}'
```

## Interactive Mode Commands

| Command | Description | Example |
|---------|-------------|---------|
| `connect <server>` | Connect to a specific server | `connect kali` |
| `disconnect` | Disconnect from current server | `disconnect` |
| `list` | List available tools | `list` |
| `call <tool> <args>` | Call a tool with JSON arguments | `call nmap {"target": "127.0.0.1"}` |
| `quit` / `exit` / `q` | Exit interactive mode | `quit` |

## Available Servers

| Server ID | Name | Description | Tools |
|-----------|------|-------------|-------|
| `kali` | Kali Linux MCP Server | Pentesting tools | nmap, gobuster, hydra, nikto, metasploit, shell_command |
| `zap` | ZAP MCP Server | Web application security testing | spider, active_scan, passive_scan, alerts, urls, report |
| `websearch` | WebSearch MCP Server | Web search functionality | search, search_news, search_images |
| `rag` | RAG MCP Server | RAG knowledge base operations | search, store, list_categories, get_category, delete_item |
| `discovery` | Discovery (OWASP) MCP Server | OWASP security testing tools | spider, check_headers, check_ssl, check_open_redirects, check_sql_injection |

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--server` | `-s` | Target server for operations |
| `--tool` | `-t` | Tool name to call |
| `--args` | `-a` | JSON arguments for tool call |
| `--interactive` | `-i` | Start interactive mode |
| `--list-servers` | `-l` | List available servers |
| `--check-containers` | `-c` | Check container status |

## Troubleshooting

### Common Issues

1. **"Missing containers" error**
   ```bash
   # Start all containers
   docker-compose up -d
   ```

2. **"Failed to connect" error**
   ```bash
   # Check if containers are running
   docker ps | grep mcp-
   
   # Restart containers if needed
   docker-compose restart
   ```

3. **"Invalid JSON arguments" error**
   - Ensure arguments are valid JSON
   - Use single quotes around the JSON string
   - Escape quotes properly

4. **"Tool not found" error**
   - Use `list` command to see available tools
   - Check tool name spelling
   - Verify you're connected to the right server

### Debug Mode

For detailed debugging, you can modify the CLI script to add more verbose logging:

```python
# Add to the top of mcp_cli.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Test Suite

This CLI complements the automated test suite in the `tests/` directory:

- **CLI**: Manual testing and debugging
- **Test Suite**: Automated regression testing

Use the CLI for:
- Exploring new features
- Debugging issues
- Manual verification
- Learning tool capabilities

Use the test suite for:
- Automated testing
- CI/CD integration
- Regression testing
- Batch testing

## Examples for Each Server

### Kali Linux Examples
```bash
# Network scanning
python mcp_cli.py -s kali -t nmap -a '{"target": "192.168.1.0/24", "options": "-sV -sC"}'

# Directory enumeration
python mcp_cli.py -s kali -t gobuster -a '{"url": "https://target.com", "wordlist": "/usr/share/wordlists/dirb/common.txt"}'

# Password cracking
python mcp_cli.py -s kali -t hydra -a '{"target": "192.168.1.1", "service": "ssh", "username": "admin"}'
```

### ZAP Examples
```bash
# Spider a website
python mcp_cli.py -s zap -t spider -a '{"url": "https://target.com", "max_depth": 3}'

# Get high-risk alerts
python mcp_cli.py -s zap -t alerts -a '{"risk_level": "High"}'

# Generate report
python mcp_cli.py -s zap -t report -a '{"format": "html"}'
```

### WebSearch Examples
```bash
# General search
python mcp_cli.py -s websearch -t search -a '{"query": "OWASP Top 10", "max_results": 5}'

# News search
python mcp_cli.py -s websearch -t search_news -a '{"query": "data breach", "max_results": 3}'

# Image search
python mcp_cli.py -s websearch -t search_images -a '{"query": "security", "max_results": 3}'
```

### RAG Examples
```bash
# Search knowledge base
python mcp_cli.py -s rag -t search -a '{"query": "penetration testing", "max_results": 5}'

# Store new information
python mcp_cli.py -s rag -t store -a '{"category": "vulnerabilities", "content": "SQL injection is a common web vulnerability"}'

# List categories
python mcp_cli.py -s rag -t list_categories -a '{}'
```

### Discovery Examples
```bash
# Spider website
python mcp_cli.py -s discovery -t spider -a '{"url": "https://target.com", "max_urls": 10}'

# Check security headers
python mcp_cli.py -s discovery -t check_headers -a '{"url": "https://target.com"}'

# Check SSL configuration
python mcp_cli.py -s discovery -t check_ssl -a '{"url": "https://target.com"}'
``` 