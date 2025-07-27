#!/usr/bin/env python3
"""
Real MCP Client Node using FastMCP library.
This replaces the fake HTTP-based MCP implementation.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from fastmcp import Client

class RealMCPClientNode:
    """Real MCP Client that communicates with proper MCP servers."""
    
    def __init__(self, output_dir: str, job_id: str, mcp_servers: Dict[str, str] = None):
        self.output_dir = output_dir
        self.job_id = job_id
        # mcp_servers: dict mapping tool name to MCP server command
        self.mcp_servers = mcp_servers or {
            'kali': 'docker exec -i mcp-kali python3 kali_server.py',
            'zap': 'docker exec -i mcp-zap python3 zap_server.py',
            'websearch': 'docker exec -i mcp-websearch python websearch_server.py',
            'rag': 'docker exec -i mcp-rag python rag_server.py',
        }
        self.sessions = {}
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run an MCP tool using proper MCP protocol."""
        tool = input_data.get('tool')
        command = input_data.get('command')
        
        if tool not in self.mcp_servers:
            return {
                'node': 'RealMCPClientNode', 
                'output': f'[ERROR] Unknown MCP tool: {tool}'
            }
        
        try:
            # Parse command into MCP tool call
            tool_name, arguments = self._parse_command_to_mcp(tool, command)
            
            # Get or create MCP session
            session = await self._get_mcp_session(tool)
            
            # Call the tool
            result = await session.call_tool(tool_name, arguments)
            
            # Extract content from result
            if result and hasattr(result, 'text'):
                output = result.text
            else:
                output = "No content returned from MCP tool"
            
            return {
                'node': 'RealMCPClientNode',
                'output': output
            }
            
        except Exception as e:
            return {
                'node': 'RealMCPClientNode',
                'output': f'[MCP ERROR] {e}'
            }
    
    def _parse_command_to_mcp(self, tool: str, command: str) -> tuple[str, Dict[str, Any]]:
        """Parse a command string into MCP tool name and arguments."""
        if tool == 'kali':
            # Parse Kali commands like "nmap -sV 192.168.1.1"
            parts = command.split()
            if parts[0] == 'nmap':
                return 'nmap', {
                    'target': parts[-1],
                    'options': ' '.join(parts[1:-1]) if len(parts) > 2 else '-sV -sC'
                }
            elif parts[0] == 'gobuster':
                return 'gobuster', {
                    'url': parts[2] if len(parts) > 2 else '',
                    'wordlist': parts[4] if len(parts) > 4 else '/usr/share/wordlists/dirb/common.txt'
                }
            elif parts[0] == 'hydra':
                return 'hydra', {
                    'target': parts[2] if len(parts) > 2 else '',
                    'service': parts[3] if len(parts) > 3 else 'ssh'
                }
            elif parts[0] == 'nikto':
                return 'nikto', {
                    'url': parts[1] if len(parts) > 1 else ''
                }
            else:
                return 'shell_command', {'command': command}
        
        elif tool == 'zap':
            # Parse ZAP commands
            if 'spider' in command.lower():
                import re
                url_match = re.search(r'https?://[^\s]+', command)
                if url_match:
                    return 'spider', {'url': url_match.group(0)}
            elif 'active' in command.lower() and 'scan' in command.lower():
                import re
                url_match = re.search(r'https?://[^\s]+', command)
                if url_match:
                    return 'active_scan', {'url': url_match.group(0)}
            elif 'passive' in command.lower() and 'scan' in command.lower():
                import re
                url_match = re.search(r'https?://[^\s]+', command)
                if url_match:
                    return 'passive_scan', {'url': url_match.group(0)}
            elif 'alerts' in command.lower():
                return 'alerts', {}
            elif 'urls' in command.lower():
                return 'urls', {}
            elif 'report' in command.lower():
                return 'report', {}
            else:
                return 'alerts', {}  # Default to alerts
        
        elif tool == 'websearch':
            return 'search', {'query': command}
        
        elif tool == 'rag':
            return 'retrieve', {'query': command}
        
        # Default fallback
        return 'execute', {'command': command}
    
    async def _get_mcp_session(self, tool: str):
        """Get or create an MCP session for the specified tool."""
        if tool not in self.sessions:
            server_command = self.mcp_servers[tool]
            
            # Create FastMCP client
            client = Client(server_command)
            await client.__aenter__()
            self.sessions[tool] = client
        
        return self.sessions[tool]
    
    async def list_tools(self, tool: str) -> List[dict]:
        """List available tools from an MCP server."""
        try:
            session = await self._get_mcp_session(tool)
            return await session.list_tools()
        except Exception as e:
            print(f"Error listing tools for {tool}: {e}")
            return []
    
    async def cleanup(self):
        """Clean up MCP sessions."""
        for tool, session in self.sessions.items():
            try:
                await session.__aexit__(None, None, None)
            except:
                pass
        self.sessions.clear()

# Example usage and testing
async def test_mcp_client():
    """Test the MCP client with a simple command."""
    client = RealMCPClientNode("/tmp", "test-job")
    
    try:
        # Test Kali MCP
        result = await client.run({
            'tool': 'kali',
            'command': 'nmap -sV 127.0.0.1'
        })
        print("Kali MCP Result:", result)
        
        # Test ZAP MCP
        result = await client.run({
            'tool': 'zap',
            'command': 'alerts'
        })
        print("ZAP MCP Result:", result)
        
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(test_mcp_client()) 