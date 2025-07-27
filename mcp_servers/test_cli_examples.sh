#!/bin/bash
# Test script for MCP CLI - Example commands

echo "🧪 MCP CLI Test Examples"
echo "========================"

# Check container status
echo "1. Checking container status..."
poetry run python mcp_cli.py --check-containers

echo -e "\n2. Listing available servers..."
poetry run python mcp_cli.py --list-servers

echo -e "\n3. Testing WebSearch server (list tools)..."
poetry run python mcp_cli.py -s websearch

echo -e "\n4. Testing RAG server (list tools)..."
poetry run python mcp_cli.py -s rag

echo -e "\n5. Testing Discovery server (list tools)..."
poetry run python mcp_cli.py -s discovery

echo -e "\n6. Testing Kali server (list tools)..."
poetry run python mcp_cli.py -s kali

echo -e "\n7. Testing ZAP server (list tools)..."
poetry run python mcp_cli.py -s zap

echo -e "\n✅ CLI test examples completed!"
echo -e "\n💡 For interactive mode, run: poetry run python mcp_cli.py -i"
echo -e "💡 For tool testing, run: poetry run python mcp_cli.py -s <server> -t <tool> -a '<json_args>'" 