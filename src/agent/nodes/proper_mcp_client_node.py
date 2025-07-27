#!/usr/bin/env python3
"""
Proper MCP Client Node that follows the actual Model Context Protocol.
This replaces the HTTP-based fake MCP implementation.
"""

import asyncio
import json
import subprocess
import sys
from typing import Any, Dict, List, Optional

class MCPRequest:
    def __init__(self, method: str, params: Dict[str, Any], id: str = None):
        self.jsonrpc = "2.0"
        self.id = id or str(hash(method + str(params)))
        self.method = method
        self.params = params
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "jsonrpc": self.jsonrpc,
            "id": self.id,
            "method": self.method,
            "params": self.params
        }

class ProperMCPClientNode:
    """Proper MCP Client that communicates with real MCP servers."""
    
    def __init__(self, output_dir: str, job_id: str, mcp_servers: Dict[str, str] = None):
        self.output_dir = output_dir
        self.job_id = job_id
        # mcp_servers: dict mapping tool name to MCP server command
        self.mcp_servers = mcp_servers or {
            'kali': 'python /app/kali_mcp_server.py',
            'zap': 'python /app/zap_mcp_server.py',
            'websearch': 'python /app/websearch_mcp_server.py',
            'rag': 'python /app/rag_mcp_server.py',
        }
        self.server_processes = {}
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run an MCP tool using proper MCP protocol."""
        tool = input_data.get('tool')
        command = input_data.get('command')
        
        if tool not in self.mcp_servers:
            return {
                'node': 'ProperMCPClientNode', 
                'output': f'[ERROR] Unknown MCP tool: {tool}'
            }
        
        try:
            # Parse command into MCP tool call
            tool_name, arguments = self._parse_command_to_mcp(tool, command)
            
            # Create MCP request
            request = MCPRequest(
                method="tools/call",
                params={
                    "name": tool_name,
                    "arguments": arguments
                }
            )
            
            # Send request to MCP server
            response = await self._send_mcp_request(tool, request)
            
            return {
                'node': 'ProperMCPClientNode',
                'output': response
            }
            
        except Exception as e:
            return {
                'node': 'ProperMCPClientNode',
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
            else:
                return 'metasploit', {'command': command}
        
        elif tool == 'zap':
            # Parse ZAP commands
            if 'spider' in command.lower():
                import re
                url_match = re.search(r'https?://[^\s]+', command)
                if url_match:
                    return 'spider', {'url': url_match.group(0)}
            elif 'scan' in command.lower():
                import re
                url_match = re.search(r'https?://[^\s]+', command)
                if url_match:
                    return 'active_scan', {'url': url_match.group(0)}
            else:
                return 'alerts', {}
        
        # Default fallback
        return 'execute', {'command': command}
    
    async def _send_mcp_request(self, tool: str, request: MCPRequest) -> str:
        """Send an MCP request to the appropriate server."""
        server_command = self.mcp_servers[tool]
        
        # Start MCP server process if not already running
        if tool not in self.server_processes:
            self.server_processes[tool] = await self._start_mcp_server(server_command)
        
        process = self.server_processes[tool]
        
        try:
            # Send request to stdin
            request_json = json.dumps(request.to_dict()) + '\n'
            process.stdin.write(request_json.encode())
            await process.stdin.drain()
            
            # Read response from stdout
            response_line = await process.stdout.readline()
            response_data = json.loads(response_line.decode().strip())
            
            # Extract content from MCP response
            if 'result' in response_data and 'content' in response_data['result']:
                content = response_data['result']['content']
                if content and len(content) > 0:
                    return content[0].get('text', '')
                else:
                    return 'No content returned'
            elif 'error' in response_data:
                return f"MCP Error: {response_data['error'].get('message', 'Unknown error')}"
            else:
                return str(response_data)
                
        except Exception as e:
            return f"Communication error with MCP server: {str(e)}"
    
    async def _start_mcp_server(self, command: str) -> asyncio.subprocess.Process:
        """Start an MCP server process."""
        try:
            process = await asyncio.create_subprocess_exec(
                *command.split(),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send initialize request
            init_request = MCPRequest(
                method="initialize",
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "pentest-agent",
                        "version": "1.0.0"
                    }
                }
            )
            
            init_json = json.dumps(init_request.to_dict()) + '\n'
            process.stdin.write(init_json.encode())
            await process.stdin.drain()
            
            # Read initialize response
            await process.stdout.readline()
            
            return process
            
        except Exception as e:
            raise Exception(f"Failed to start MCP server '{command}': {str(e)}")
    
    async def cleanup(self):
        """Clean up MCP server processes."""
        for tool, process in self.server_processes.items():
            try:
                process.terminate()
                await process.wait()
            except:
                pass
        self.server_processes.clear()

# Example usage
async def main():
    client = ProperMCPClientNode("/tmp", "test-job")
    
    # Test MCP call
    result = await client.run({
        'tool': 'kali',
        'command': 'nmap -sV 192.168.1.1'
    })
    
    print(result)
    await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 