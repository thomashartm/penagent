#!/usr/bin/env python3
"""
Proper MCP Server for Kali Linux tools using the actual MCP protocol.
This follows the Model Context Protocol specification.
"""

import asyncio
import json
import subprocess
import sys
from typing import Any, Dict, List, Optional

# MCP Protocol Types
class MCPRequest:
    def __init__(self, jsonrpc: str, id: str, method: str, params: Dict[str, Any]):
        self.jsonrpc = jsonrpc
        self.id = id
        self.method = method
        self.params = params

class MCPResponse:
    def __init__(self, jsonrpc: str, id: str, result: Any = None, error: Dict[str, Any] = None):
        self.jsonrpc = jsonrpc
        self.id = id
        self.result = result
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        response = {"jsonrpc": self.jsonrpc, "id": self.id}
        if self.result is not None:
            response["result"] = self.result
        if self.error is not None:
            response["error"] = self.error
        return response

class KaliMCPServer:
    """Proper MCP Server for Kali Linux pentesting tools."""
    
    def __init__(self):
        self.tools = {
            "nmap": {
                "name": "nmap",
                "description": "Network discovery and security auditing",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string", "description": "Target host or network"},
                        "options": {"type": "string", "description": "Nmap options"}
                    },
                    "required": ["target"]
                }
            },
            "metasploit": {
                "name": "metasploit",
                "description": "Penetration testing framework",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Metasploit command"}
                    },
                    "required": ["command"]
                }
            },
            "gobuster": {
                "name": "gobuster",
                "description": "Directory/file enumeration tool",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target URL"},
                        "wordlist": {"type": "string", "description": "Wordlist path"}
                    },
                    "required": ["url"]
                }
            }
        }
    
    async def handle_request(self, request_data: str) -> str:
        """Handle MCP protocol requests."""
        try:
            request = json.loads(request_data)
            request_obj = MCPRequest(
                jsonrpc=request.get("jsonrpc", "2.0"),
                id=request.get("id"),
                method=request.get("method"),
                params=request.get("params", {})
            )
            
            if request_obj.method == "initialize":
                return self._handle_initialize(request_obj)
            elif request_obj.method == "tools/list":
                return self._handle_tools_list(request_obj)
            elif request_obj.method == "tools/call":
                return self._handle_tools_call(request_obj)
            else:
                return self._create_error_response(request_obj.id, -32601, "Method not found")
                
        except json.JSONDecodeError:
            return self._create_error_response(None, -32700, "Parse error")
        except Exception as e:
            return self._create_error_response(request_obj.id if 'request_obj' in locals() else None, -32603, str(e))
    
    def _handle_initialize(self, request: MCPRequest) -> str:
        """Handle MCP initialize request."""
        response = MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            result={
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "kali-mcp-server",
                    "version": "1.0.0"
                }
            }
        )
        return json.dumps(response.to_dict())
    
    def _handle_tools_list(self, request: MCPRequest) -> str:
        """Handle MCP tools/list request."""
        tools_list = []
        for tool_id, tool_info in self.tools.items():
            tools_list.append({
                "name": tool_id,
                "description": tool_info["description"],
                "inputSchema": tool_info["inputSchema"]
            })
        
        response = MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            result={"tools": tools_list}
        )
        return json.dumps(response.to_dict())
    
    def _handle_tools_call(self, request: MCPRequest) -> str:
        """Handle MCP tools/call request."""
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        
        if tool_name not in self.tools:
            return self._create_error_response(request.id, -32602, f"Tool '{tool_name}' not found")
        
        try:
            # Execute the tool command
            result = self._execute_tool(tool_name, arguments)
            
            response = MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            )
            return json.dumps(response.to_dict())
            
        except Exception as e:
            return self._create_error_response(request.id, -32603, f"Tool execution failed: {str(e)}")
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a Kali Linux tool with the given arguments."""
        if tool_name == "nmap":
            target = arguments.get("target")
            options = arguments.get("options", "-sV -sC")
            command = f"nmap {options} {target}"
        elif tool_name == "metasploit":
            command = arguments.get("command")
        elif tool_name == "gobuster":
            url = arguments.get("url")
            wordlist = arguments.get("wordlist", "/usr/share/wordlists/dirb/common.txt")
            command = f"gobuster dir -u {url} -w {wordlist}"
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Execute command in Kali container
        try:
            result = subprocess.run(
                ["docker", "exec", "mcp-kali", "/bin/bash", "-c", command],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            output = f"Command: {command}\n"
            output += f"Exit Code: {result.returncode}\n"
            output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            
            return output
            
        except subprocess.TimeoutExpired:
            return f"Command timed out: {command}"
        except Exception as e:
            return f"Execution error: {str(e)}"
    
    def _create_error_response(self, request_id: Optional[str], code: int, message: str) -> str:
        """Create an MCP error response."""
        response = MCPResponse(
            jsonrpc="2.0",
            id=request_id,
            error={
                "code": code,
                "message": message
            }
        )
        return json.dumps(response.to_dict())

async def main():
    """Main MCP server loop."""
    server = KaliMCPServer()
    
    # MCP servers communicate via stdio
    while True:
        try:
            # Read request from stdin
            request_data = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not request_data:
                break
            
            # Handle request
            response = await server.handle_request(request_data.strip())
            
            # Write response to stdout
            await asyncio.get_event_loop().run_in_executor(None, lambda: sys.stdout.write(response + "\n"))
            await asyncio.get_event_loop().run_in_executor(None, sys.stdout.flush)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            error_response = server._create_error_response(None, -32603, f"Server error: {str(e)}")
            await asyncio.get_event_loop().run_in_executor(None, lambda: sys.stdout.write(error_response + "\n"))
            await asyncio.get_event_loop().run_in_executor(None, sys.stdout.flush)

if __name__ == "__main__":
    asyncio.run(main()) 