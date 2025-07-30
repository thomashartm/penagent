#!/bin/bash

# Script to start a conversation with the security orchestration CLI

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if services are running
echo -e "${BLUE}[INFO]${NC} Checking required services..."
./start_services.sh status > /dev/null 2>&1 || {
    echo -e "${BLUE}[INFO]${NC} Starting required services..."
    ./start_services.sh start
}

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    echo -e "${RED}[ERROR]${NC} Please run this script from the project root directory"
    exit 1
fi

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Poetry is not installed. Please install poetry first."
    exit 1
fi

# Install dependencies if needed
echo -e "${BLUE}[INFO]${NC} Ensuring dependencies are installed..."
poetry install --quiet

# Main chat loop
echo -e "${GREEN}Security Orchestration Chat CLI${NC}"
echo "Type your message and press Enter. Type 'exit' or 'quit' to leave."
echo "You can also use commands like:"
echo "  - scan <target> [--message <message>] [--verbose]"
echo "  - status <job_id>"
echo "  - history [--limit <number>]"
echo "  - cancel <job_id>"
echo ""

while true; do
    echo -n -e "${BLUE}You > ${NC}"
    read -r user_input
    
    # Handle exit commands
    if [[ "$user_input" == "exit" || "$user_input" == "quit" ]]; then
        echo -e "${GREEN}Goodbye!${NC}"
        break
    fi
    
    # Handle empty input
    if [[ -z "$user_input" ]]; then
        continue
    fi
    
    # Handle help command
    if [[ "$user_input" == "help" ]]; then
        echo -e "${YELLOW}Available commands:${NC}"
        echo "  chat <message> - Chat with the AI assistant"
        echo "  scan <target> [--message <message>] [--verbose] - Run security scan"
        echo "  status <job_id> - Check job status"
        echo "  history [--limit <number>] - Show job history"
        echo "  cancel <job_id> - Cancel a running job"
        echo "  help - Show this help message"
        echo "  exit/quit - Exit the chat"
        echo ""
        continue
    fi
    
    # Handle scan command
    if [[ "$user_input" =~ ^scan[[:space:]]+([^[:space:]]+)(.*)$ ]]; then
        target="${BASH_REMATCH[1]}"
        remaining="${BASH_REMATCH[2]}"
        
        # Parse optional arguments
        message=""
        verbose=""
        
        if [[ "$remaining" =~ --message[[:space:]]+([^[:space:]]+) ]]; then
            message="--message ${BASH_REMATCH[1]}"
        fi
        
        if [[ "$remaining" =~ --verbose ]]; then
            verbose="--verbose"
        fi
        
        echo -e "${BLUE}[INFO]${NC} Starting security scan for target: $target"
        poetry run python -m core.cli scan "$target" $message $verbose
        echo ""
        continue
    fi
    
    # Handle status command
    if [[ "$user_input" =~ ^status[[:space:]]+([^[:space:]]+)$ ]]; then
        job_id="${BASH_REMATCH[1]}"
        echo -e "${BLUE}[INFO]${NC} Checking status for job: $job_id"
        poetry run python -m core.cli status "$job_id"
        echo ""
        continue
    fi
    
    # Handle history command
    if [[ "$user_input" =~ ^history(.*)$ ]]; then
        remaining="${BASH_REMATCH[1]}"
        limit=""
        
        if [[ "$remaining" =~ --limit[[:space:]]+([0-9]+) ]]; then
            limit="--limit ${BASH_REMATCH[1]}"
        fi
        
        echo -e "${BLUE}[INFO]${NC} Showing job history..."
        poetry run python -m core.cli history $limit
        echo ""
        continue
    fi
    
    # Handle cancel command
    if [[ "$user_input" =~ ^cancel[[:space:]]+([^[:space:]]+)$ ]]; then
        job_id="${BASH_REMATCH[1]}"
        echo -e "${BLUE}[INFO]${NC} Cancelling job: $job_id"
        poetry run python -m core.cli cancel "$job_id"
        echo ""
        continue
    fi
    
    # Default: treat as chat message
    echo -e "${BLUE}[INFO]${NC} Sending message to AI assistant..."
    poetry run python -m core.cli chat "$user_input"
    echo ""
done 