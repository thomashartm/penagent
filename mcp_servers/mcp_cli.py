#!/usr/bin/env python3
"""
MCP Servers CLI - Manual Testing and Debugging Tool
A comprehensive CLI for probing MCP servers and sending test payloads.
"""

import asyncio
import json
import sys
import argparse
from typing import Dict, List, Any, Optional
from fastmcp import Client
import subprocess

class MCPServerCLI:
    """CLI for testing and debugging MCP servers."""
    
    def __init__(self):
        self.servers = {
            'kali': {
                'name': 'Kali Linux MCP Server',
                'command': 'docker',
                'args': ['exec', '-i', 'mcp-kali', 'python3', 'kali_server.py'],
                'description': 'Pentesting tools (nmap, gobuster, hydra, etc.)'
            },
            'zap': {
                'name': 'ZAP MCP Server', 
                'command': 'docker',
                'args': ['exec', '-i', 'mcp-zap', 'python3', 'zap_server.py'],
                'description': 'Web application security testing'
            },
            'websearch': {
                'name': 'WebSearch MCP Server',
                'command': 'docker',
                'args': ['exec', '-i', 'mcp-websearch', 'python', 'websearch_server.py'], 
                'description': 'Web search functionality'
            },
            'rag': {
                'name': 'RAG MCP Server',
                'command': 'docker',
                'args': ['exec', '-i', 'mcp-rag', 'python', 'rag_server.py'],
                'description': 'RAG knowledge base operations'
            },
            'discovery': {
                'name': 'Discovery (OWASP) MCP Server',
                'command': 'docker',
                'args': ['exec', '-i', 'mcp-discovery', 'python', 'owasp_server.py'],
                'description': 'OWASP security testing tools'
            }
        }
        self.client = None
        self.current_server = None
    
    async def check_containers(self) -> bool:
        """Check if required containers are running."""
        print("🔍 Checking container status...")
        
        try:
            result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                                  capture_output=True, text=True)
            running_containers = result.stdout.strip().split('\n')
            
            missing = []
            for server_id, server_info in self.servers.items():
                container_name = f"mcp-{server_id}"
                if container_name not in running_containers:
                    missing.append(container_name)
            
            if missing:
                print(f"❌ Missing containers: {', '.join(missing)}")
                print("💡 Start containers with: docker-compose up -d")
                return False
            
            print("✅ All containers are running")
            return True
            
        except Exception as e:
            print(f"❌ Error checking containers: {e}")
            return False
    
    async def connect_to_server(self, server_id: str) -> bool:
        """Connect to a specific MCP server."""
        if server_id not in self.servers:
            print(f"❌ Unknown server: {server_id}")
            return False
        
        try:
            server_info = self.servers[server_id]
            print(f"🔌 Connecting to {server_info['name']}...")
            
            # Create FastMCP client with stdio transport
            from fastmcp.client import Client
            from fastmcp.client.transports import StdioTransport
            
            transport = StdioTransport(server_info['command'], server_info['args'])
            self.client = Client(transport)
            await self.client.__aenter__()
            self.current_server = server_id
            
            # Test connection with initialize
            print(f"✅ Connected to {server_info['name']}")
            # Optionally print a generic connected message or skip
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to {server_id}: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from current server."""
        if self.client:
            await self.client.__aexit__(None, None, None)
            self.client = None
            self.current_server = None
            print("🔌 Disconnected")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from current server."""
        if not self.client:
            print("❌ Not connected to any server")
            return []
        
        try:
            tools = await self.client.list_tools()
            if not tools or not isinstance(tools, list):
                print("❌ Error listing tools: No tools found or unexpected response.")
                print("📋 Found 0 tools:\n")
            else:
                print(f"📋 Found {len(tools)} tools:\n")
                for tool in tools:
                    # FastMCP 2.x returns Tool objects, use attribute access
                    name = getattr(tool, 'name', str(tool))
                    desc = getattr(tool, 'description', '')
                    print(f"- {name}: {desc}")
            return tools
        except Exception as e:
            print(f"❌ Error listing tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """Call a specific tool with arguments."""
        if not self.client:
            print("❌ Not connected to any server")
            return None
        
        try:
            result = await self.client.call_tool(tool_name, arguments)
            return result.text if hasattr(result, 'text') else str(result)
        except Exception as e:
            print(f"❌ Error calling tool {tool_name}: {e}")
            return None
    
    async def interactive_mode(self):
        """Interactive mode for testing."""
        print("\n🎯 Interactive Mode")
        print("Commands: list, call <tool> <args>, connect <server>, disconnect, quit")
        print("Example: call nmap {'target': '127.0.0.1'}")
        
        while True:
            try:
                if self.current_server:
                    prompt = f"mcp[{self.current_server}]> "
                else:
                    prompt = "mcp> "
                
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                
                if command.lower() == 'disconnect':
                    await self.disconnect()
                    continue
                
                if command.lower() == 'list':
                    tools = await self.list_tools()
                    if tools:
                        print(f"\n📋 Available tools ({len(tools)}):")
                        for tool in tools:
                            print(f"   • {tool['name']}: {tool['description']}")
                    else:
                        print("❌ No tools available")
                    continue
                
                if command.startswith('connect '):
                    server_id = command.split(' ', 1)[1]
                    await self.connect_to_server(server_id)
                    continue
                
                if command.startswith('call '):
                    parts = command.split(' ', 2)
                    if len(parts) < 3:
                        print("❌ Usage: call <tool_name> <json_arguments>")
                        continue
                    
                    tool_name = parts[1]
                    try:
                        arguments = json.loads(parts[2])
                        print(f"🔧 Calling {tool_name} with arguments: {arguments}")
                        result = await self.call_tool(tool_name, arguments)
                        if result:
                            print(f"✅ Result:\n{result}")
                        else:
                            print("❌ No result returned")
                    except json.JSONDecodeError:
                        print("❌ Invalid JSON arguments")
                    continue
                
                print("❌ Unknown command. Use: list, call, connect, disconnect, quit")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        await self.disconnect()
    
    async def quick_test(self, server_id: str, tool_name: str = None, arguments: Dict[str, Any] = None):
        """Quick test of a server with optional tool call."""
        print(f"🧪 Quick test for {server_id}")
        
        if not await self.connect_to_server(server_id):
            return
        
        try:
            # List tools
            tools = await self.list_tools()
            print(f"📋 Found {len(tools)} tools:")
            for tool in tools:
                print(f"   • {getattr(tool, 'name', str(tool))}: {getattr(tool, 'description', '')}")
            
            # Call specific tool if provided
            if tool_name and arguments:
                print(f"\n🔧 Testing tool: {tool_name}")
                result = await self.call_tool(tool_name, arguments)
                if result:
                    print(f"✅ Tool result:\n{result}")
                else:
                    print("❌ Tool call failed")
        
        finally:
            await self.disconnect()
    
    def print_server_info(self):
        """Print information about available servers."""
        print("📋 Available MCP Servers:")
        print("=" * 60)
        for server_id, info in self.servers.items():
            print(f"• {server_id}: {info['name']}")
            print(f"  {info['description']}")
            print()

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='MCP Servers CLI - Testing and Debugging Tool')
    parser.add_argument('--server', '-s', choices=['kali', 'zap', 'websearch', 'rag', 'discovery'],
                       help='Target server for operations')
    parser.add_argument('--tool', '-t', help='Tool name to call')
    parser.add_argument('--args', '-a', help='JSON arguments for tool call')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Start interactive mode')
    parser.add_argument('--list-servers', '-l', action='store_true',
                       help='List available servers')
    parser.add_argument('--check-containers', '-c', action='store_true',
                       help='Check container status')
    
    args = parser.parse_args()
    
    cli = MCPServerCLI()
    
    async def run():
        # Check containers first
        #if not await cli.check_containers():
        #    return
        
        if args.list_servers:
            cli.print_server_info()
            return
        
        #if args.check_containers:
        #    print("✅ All containers are running")
        #    return
        
        if args.interactive:
            await cli.interactive_mode()
            return
        
        if args.server:
            arguments = None
            if args.args:
                try:
                    arguments = json.loads(args.args)
                except json.JSONDecodeError:
                    print("❌ Invalid JSON arguments")
                    return
            
            await cli.quick_test(args.server, args.tool, arguments)
            return
        
        # Default: show help
        cli.print_server_info()
        print("💡 Use --interactive for interactive mode")
        print("💡 Use --server <name> --tool <name> --args <json> for quick test")
    
    asyncio.run(run())

if __name__ == "__main__":
    main() 