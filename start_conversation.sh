#!/bin/bash

# Script to start a conversation with the security orchestration CLI

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if services are running
./start_services.sh status > /dev/null 2>&1 || {
    echo -e "${BLUE}[INFO]${NC} Starting required services..."
    ./start_services.sh start
}

# Activate poetry environment if needed
to_poetry() {
    if command -v poetry &> /dev/null; then
        echo "poetry run $1"
    else
        echo "$1"
    fi
}

# Main chat loop
echo -e "${GREEN}Security Orchestration Chat CLI${NC}"
echo "Type your message and press Enter. Type 'exit' or 'quit' to leave."

while true; do
    echo -n -e "${BLUE}You > ${NC}"
    read -r user_input
    if [[ "$user_input" == "exit" || "$user_input" == "quit" ]]; then
        echo "Goodbye!"
        break
    fi
    if [[ -z "$user_input" ]]; then
        continue
    fi
    # Run the chat command
    poetry run python -m core.cli chat "$user_input"
done 