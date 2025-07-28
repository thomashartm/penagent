# Security Testing Orchestration Core

Core LangGraph orchestration system for security testing phases.

## Overview

This project implements an intelligent security testing orchestration system using LangGraph and LangChain. The system can:

- Process user input and decide whether to engage in conversation or initiate security testing
- Orchestrate different security testing phases (information gathering, spidering, active scanning, evaluation reporting)
- Use MCP clients to execute tools from the mcp_servers project
- Apply different strategies for each phase using prepared prompts

## Architecture

### Components

1. **Input Processor**: LLM that decides whether to chat or initiate security testing
2. **Phase Orchestrator**: LangGraph workflow that manages different security testing phases
3. **MCP Client Manager**: Handles connections to Kali, WebSearch, and RAG MCP servers
4. **Strategy Prompts**: Pre-defined prompts for different security testing phases
5. **CLI Interface**: Simple command-line interface for user interaction

### Security Testing Phases

1. **Information Gathering**: Reconnaissance and target discovery
2. **Spidering**: Web application crawling and mapping
3. **Active Scanning**: Vulnerability scanning and assessment
4. **Evaluation & Reporting**: Analysis and report generation

## Project Structure

```
core/
├── __init__.py
├── cli.py                 # CLI entrypoint
├── orchestrator.py        # LangGraph workflow orchestration
├── mcp_client.py         # MCP client management
├── models.py            # Pydantic models for data structures
├── strategies/           # Security testing strategy prompts
│   ├── __init__.py
│   ├── information_gathering.py
│   ├── spidering.py
│   ├── active_scanning.py
│   └── evaluation.py
├── demo.py              # Demonstration script
└── test_basic.py        # Basic test script
```

## Setup Instructions

### 1. Install Dependencies

```bash
# Navigate to the core directory
cd core

# Install dependencies (if poetry.lock exists)
poetry install

# Or install dependencies without lock file
poetry install --no-cache
```

### 2. Start MCP Servers

```bash
# Navigate to mcp_servers directory
cd ../mcp_servers

# Start all MCP servers
docker-compose up -d

# Verify servers are running
docker-compose ps
```

### 3. Set Environment Variables

```bash
# Set OpenAI API key (required for LLM functionality)
export OPENAI_API_KEY="your-openai-api-key"

# Or create a .env file
echo "OPENAI_API_KEY=your-openai-api-key" > .env
```

## Usage

### CLI Commands

```bash
# Security scanning
python -m core.cli scan example.com
python -m core.cli scan example.com --message "Focus on web vulnerabilities"
python -m core.cli scan example.com --verbose

# Chat mode
python -m core.cli chat "Hello, how can you help me?"
python -m core.cli chat "What security testing capabilities do you have?"

# Help
python -m core.cli --help
python -m core.cli scan --help
python -m core.cli chat --help
```

### Programmatic Usage

```python
from core.orchestrator import SecurityOrchestrator

# Initialize orchestrator
orchestrator = SecurityOrchestrator(llm_model="gpt-4")

# Run security scan
final_state = await orchestrator.run_workflow(
    "Conduct comprehensive security assessment of example.com",
    target="example.com"
)

# Access results
print(f"Intent: {final_state.intent_decision.intent}")
print(f"Phases completed: {len(final_state.phase_results)}")
print(f"Final report: {final_state.final_report}")
```

## Security Testing Workflow

### 1. Intent Detection
The system analyzes user input to determine if they want to:
- **CHAT**: Have a conversation or get information
- **SECURITY_TESTING**: Conduct security testing

### 2. Security Testing Phases

#### Information Gathering
- **Tools**: nmap, sublist3r, whatweb, google_dork, websearch, rag_search
- **Objectives**: Discover infrastructure, identify subdomains, gather public information
- **Output**: Network map, service inventory, technology stack

#### Spidering
- **Tools**: gobuster, nikto, whatweb, websearch, rag_store
- **Objectives**: Map web applications, discover endpoints, identify technologies
- **Output**: Web application structure, endpoint inventory

#### Active Scanning
- **Tools**: nuclei, nikto, hydra, metasploit, websearch, rag_store
- **Objectives**: Test for vulnerabilities, validate security issues
- **Output**: Vulnerability findings, security assessment

#### Evaluation
- **Tools**: rag_search, rag_get_category, websearch, shell_command
- **Objectives**: Analyze findings, generate report, provide recommendations
- **Output**: Comprehensive security assessment report

### 3. MCP Integration

The system uses FastMCP to connect to:
- **Kali MCP Server**: Pentesting tools (nmap, gobuster, nuclei, etc.)
- **WebSearch MCP Server**: Web search and information gathering
- **RAG MCP Server**: Knowledge base operations and findings storage

## Development

### Running Tests

```bash
# Basic structure test
python test_basic.py

# Demonstration
python demo.py
```

### Code Structure

- **models.py**: Pydantic models for data validation
- **mcp_client.py**: MCP server connections and tool execution
- **orchestrator.py**: LangGraph workflow orchestration
- **strategies/**: Phase-specific prompts and logic
- **cli.py**: Command-line interface

### Adding New Phases

1. Create strategy class in `strategies/`
2. Add phase to `SecurityPhase` enum in `models.py`
3. Update `MCPClientManager.get_phase_tools()` in `mcp_client.py`
4. Add phase to workflow in `orchestrator.py`

## Troubleshooting

### Common Issues

1. **MCP Connection Errors**
   - Ensure Docker containers are running: `docker-compose ps`
   - Check container logs: `docker-compose logs [service-name]`
   - Restart containers: `docker-compose restart`

2. **LLM API Errors**
   - Verify OPENAI_API_KEY is set
   - Check API key permissions and quota

3. **Import Errors**
   - Install dependencies: `poetry install`
   - Check Python path and virtual environment

### Debug Mode

```bash
# Run with verbose output
python -m core.cli scan example.com --verbose

# Check MCP server status
cd ../mcp_servers
docker-compose logs
```

## Next Steps

1. **Install Dependencies**: Resolve poetry installation issues
2. **Configure LLM**: Set up OpenAI API key
3. **Start MCP Servers**: Ensure all containers are running
4. **Test Basic Functionality**: Run demo and test scripts
5. **Conduct Security Assessment**: Use CLI to scan targets

## License

MIT License - see LICENSE file for details. 