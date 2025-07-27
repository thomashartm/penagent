# MCP Server Test Suite

This directory contains comprehensive test suites for all MCP servers in the project. Each test file is designed to manually test the capabilities of individual MCP servers.

## Test Files

### Individual Server Tests

- **`test_kali_mcp_server.py`** - Tests the Kali Linux MCP server
  - MCP protocol initialization
  - Tool discovery (tools/list)
  - Nmap tool execution
  - Gobuster tool execution
  - Shell command execution
  - Error handling for invalid tools/methods

- **`test_zap_mcp_server.py`** - Tests the ZAP MCP server
  - MCP protocol initialization
  - Tool discovery (tools/list)
  - Spider tool execution
  - Alerts tool execution (with and without filters)
  - URLs tool execution (with and without filters)
  - Error handling for invalid tools/methods

### Test Runner

- **`run_all_tests.py`** - Comprehensive test runner
  - Runs all individual test suites
  - Provides overall summary
  - Checks container status before running tests

## Prerequisites

Before running the tests, ensure:

1. **Containers are running:**
   ```bash
   cd mcp_servers
   docker-compose up -d kali zap
   ```

2. **Python environment is set up:**
   ```bash
   # From the project root
   poetry install
   ```

## Running Tests

### Run All Tests

To run all MCP server tests:

```bash
cd mcp_servers/tests
python run_all_tests.py
```

### Run Individual Tests

To test a specific server:

```bash
# Test Kali MCP server
python test_kali_mcp_server.py

# Test ZAP MCP server
python test_zap_mcp_server.py
```

## Test Output

Each test provides detailed output including:

- **Request/Response pairs** - Shows the exact MCP protocol messages
- **Tool execution results** - Displays actual tool output
- **Error handling** - Tests invalid requests and error responses
- **Summary report** - Overall pass/fail status

### Example Output

```
🧪 KALI MCP SERVER TEST SUITE
==================================================

🚀 Starting Kali MCP Server...
✅ Kali MCP Server started successfully

🔧 Testing MCP Initialize...
Request: {
  "jsonrpc": "2.0",
  "id": "test-init",
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "kali-mcp-tester",
      "version": "1.0.0"
    }
  }
}
Response: {
  "jsonrpc": "2.0",
  "id": "test-init",
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "serverInfo": {
      "name": "kali-mcp-server",
      "version": "1.0.0"
    }
  }
}
✅ Initialize test passed

📊 KALI MCP SERVER TEST SUMMARY
==================================================
✅ Initialize: PASS
✅ Tools List: PASS
✅ Nmap Tool: PASS
✅ Gobuster Tool: PASS
✅ Shell Command Tool: PASS
✅ Invalid Tool: PASS
✅ Invalid Method: PASS

📈 Results: 7/7 tests passed
🎉 All tests passed! Kali MCP Server is working correctly.
```

## Test Coverage

### MCP Protocol Tests

- **Initialize** - Tests MCP protocol initialization
- **Tools List** - Tests tool discovery and schema validation
- **Tool Execution** - Tests actual tool calls with various parameters
- **Error Handling** - Tests invalid tools, methods, and malformed requests

### Tool-Specific Tests

#### Kali MCP Server
- **Nmap** - Network scanning tool
- **Gobuster** - Directory enumeration tool
- **Shell Command** - Arbitrary command execution

#### ZAP MCP Server
- **Spider** - Web crawling tool
- **Alerts** - Security alert retrieval (with filtering)
- **URLs** - Discovered URL listing (with filtering)

## Troubleshooting

### Common Issues

1. **Container not running:**
   ```
   ❌ Failed to start Kali MCP Server: Container not found
   ```
   **Solution:** Start the containers first
   ```bash
   docker-compose up -d kali zap
   ```

2. **Permission errors:**
   ```
   ❌ Failed to start Kali MCP Server: Permission denied
   ```
   **Solution:** Ensure Docker is running and you have permissions

3. **MCP protocol errors:**
   ```
   ❌ Initialize test failed
   ```
   **Solution:** Check if the MCP server is properly implemented and running

### Debug Mode

To get more detailed output, you can modify the test files to include debug logging:

```python
# Add to test files for more verbose output
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Adding New Tests

To add tests for a new MCP server:

1. **Create a new test file** following the naming convention: `test_<server_name>_mcp_server.py`

2. **Follow the existing pattern:**
   ```python
   class NewMCPServerTester:
       async def start_server(self):
           # Start the server
       
       async def test_initialize(self):
           # Test MCP initialize
       
       async def test_list_tools(self):
           # Test tools list
       
       async def test_specific_tools(self):
           # Test specific tools
   ```

3. **Add to the test runner:**
   ```python
   # In run_all_tests.py
   self.test_files = [
       "test_kali_mcp_server.py",
       "test_zap_mcp_server.py",
       "test_new_mcp_server.py"  # Add your new test
   ]
   ```

## Integration with CI/CD

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Test MCP Servers
  run: |
    cd mcp_servers
    docker-compose up -d kali zap
    cd tests
    python run_all_tests.py
```

## Test Results Interpretation

- **All tests pass** - MCP server is working correctly
- **Some tests fail** - Check the specific error messages for debugging
- **All tests fail** - Likely a fundamental issue with the MCP server implementation

## Contributing

When adding new tests:

1. Follow the existing code style and patterns
2. Include comprehensive error handling
3. Add clear documentation for new test cases
4. Update this README with new test information 