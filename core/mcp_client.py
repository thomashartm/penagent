"""
MCP Client Manager for connecting to security testing MCP servers.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
import socket

from .models import MCPToolResult, SecurityPhase


class MCPClientManager:
    """Manages connections to MCP servers for security testing tools."""
    
    def __init__(self):
        self.clients: Dict[str, Client] = {}
        self.server_configs = {
            "kali": {
                "command": "docker",
                "args": ["exec", "-i", "mcp-kali", "python3", "kali_server.py"]
            },
            "websearch": {
                "command": "docker", 
                "args": ["exec", "-i", "mcp-websearch", "python3", "websearch_server.py"]
            },
            "rag": {
                "command": "docker",
                "args": ["exec", "-i", "mcp-rag", "python3", "rag_server.py"]
            }
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect_all()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect_all()
    
    async def connect_all(self) -> None:
        """Connect to all MCP servers."""
        for server_name, config in self.server_configs.items():
            try:
                transport = StdioTransport(config["command"], config["args"])
                client = Client(transport)
                await client.__aenter__()
                self.clients[server_name] = client
                print(f"✅ Connected to {server_name} MCP server")
            except Exception as e:
                print(f"❌ Failed to connect to {server_name} MCP server: {e}")
    
    async def disconnect_all(self) -> None:
        """Disconnect from all MCP servers."""
        for server_name, client in self.clients.items():
            try:
                await client.__aexit__(None, None, None)
                print(f"✅ Disconnected from {server_name} MCP server")
            except Exception as e:
                print(f"❌ Error disconnecting from {server_name}: {e}")
        self.clients.clear()
    
    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """List available tools from a specific MCP server."""
        if server_name not in self.clients:
            raise ValueError(f"Server {server_name} not connected")
        
        try:
            tools = await self.clients[server_name].list_tools()
            return [
                {
                    "name": getattr(tool, 'name', 'unknown'),
                    "description": getattr(tool, 'description', ''),
                    "server": server_name
                }
                for tool in tools
            ]
        except Exception as e:
            raise Exception(f"Failed to list tools from {server_name}: {e}")
    
    async def execute_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Execute a tool on a specific MCP server."""
        if server_name not in self.clients:
            raise ValueError(f"Server {server_name} not connected")
        
        start_time = time.time()
        try:
            result = await self.clients[server_name].call_tool(tool_name, arguments)
            
            # Extract output from CallToolResult
            output = getattr(result, 'data', None)
            if not output and hasattr(result, 'content') and result.content:
                output = getattr(result.content[0], 'text', str(result.content[0]))
            
            duration = time.time() - start_time
            
            return MCPToolResult(
                tool_name=tool_name,
                success=True,
                output=output or "No output",
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return MCPToolResult(
                tool_name=tool_name,
                success=False,
                output="",
                error=str(e),
                duration=duration
            )
    
    def get_phase_tools(self, phase: SecurityPhase) -> Dict[str, List[str]]:
        """Get the tools available for a specific security testing phase."""
        phase_tools = {
            SecurityPhase.INFORMATION_GATHERING: {
                "kali": ["nmap", "sublist3r", "whatweb", "google_dork"],
                "websearch": ["search", "search_news"],
                "rag": ["search", "list_categories"]
            },
            SecurityPhase.SPIDERING: {
                "kali": ["gobuster", "nikto", "whatweb"],
                "websearch": ["search"],
                "rag": ["search", "store"]
            },
            SecurityPhase.ACTIVE_SCANNING: {
                "kali": ["nuclei", "nikto", "hydra", "metasploit"],
                "websearch": ["search"],
                "rag": ["search", "store"]
            },
            SecurityPhase.EVALUATION: {
                "kali": ["shell_command"],
                "websearch": ["search"],
                "rag": ["search", "get_category", "list_categories"]
            }
        }
        
        return phase_tools.get(phase, {})
    
    async def execute_phase_tools(self, phase: SecurityPhase, target: str, context: Dict[str, Any] = None) -> List[MCPToolResult]:
        """Execute tools appropriate for a specific security testing phase."""
        phase_tools = self.get_phase_tools(phase)
        results = []
        
        for server_name, tools in phase_tools.items():
            for tool_name in tools:
                # Prepare arguments based on tool and phase
                arguments = self._prepare_tool_arguments(tool_name, target, phase, context or {})
                
                try:
                    result = await self.execute_tool(server_name, tool_name, arguments)
                    results.append(result)
                except Exception as e:
                    results.append(MCPToolResult(
                        tool_name=tool_name,
                        success=False,
                        output="",
                        error=str(e),
                        duration=0.0
                    ))
        
        return results
    
    def resolve_to_ip(target: str) -> str:
        """Resolve a hostname or URL to its IP address. If already an IP, return as is."""
        # Extract hostname from URL if needed
        if target.startswith("http://") or target.startswith("https://"):
            from urllib.parse import urlparse
            hostname = urlparse(target).hostname
        else:
            hostname = target
        # If already an IP, return
        try:
            socket.inet_aton(hostname)
            return hostname
        except Exception:
            pass
        # Try to resolve
        try:
            ip = socket.gethostbyname(hostname)
            return ip
        except Exception:
            return target  # fallback to original if resolution fails
    
    def _prepare_tool_arguments(self, tool_name: str, target: str, phase: SecurityPhase, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare arguments for tool execution based on tool name and phase. Only pass required arguments."""
        args = {}
        # Tools that require IP resolution
        ip_tools = {"nmap", "nuclei", "hydra"}
        ip_target = resolve_to_ip(target) if tool_name in ip_tools else target
        # Kali tools
        if tool_name == "nmap":
            args = {"target": ip_target}
            if phase == SecurityPhase.INFORMATION_GATHERING:
                args["options"] = "-sV -sC -p-"
        elif tool_name == "nuclei":
            args = {"target": ip_target}
            if phase == SecurityPhase.ACTIVE_SCANNING:
                args["template"] = "cves"
        elif tool_name == "whatweb":
            args = {"target": target}
        elif tool_name == "gobuster" or tool_name == "nikto":
            args = {"url": target if target.startswith(("http://", "https://")) else f"https://{target}"}
        elif tool_name == "sublist3r":
            args = {"domain": target}
        elif tool_name == "hydra":
            args = {"target": ip_target}
        elif tool_name == "metasploit":
            args = {"command": "help"}  # Placeholder, should be orchestrated
        elif tool_name == "shell_command":
            args = {"command": "whoami"}  # Placeholder, should be orchestrated
        elif tool_name == "google_dork":
            args = {"query": f"site:{target} inurl:admin"}
        elif tool_name == "recon-ng":
            args = {"domain": target}
        # Websearch tools
        elif tool_name == "search" or tool_name == "search_news":
            args = {"query": f"{target} security vulnerabilities"}
            if phase == SecurityPhase.EVALUATION:
                args["query"] = f"security assessment {target} findings"
        # RAG tools
        elif tool_name == "store":
            args = {"category": f"{phase.value}_{target}", "content": f"Security testing results for {target} in {phase.value} phase"}
        elif tool_name == "get_category":
            args = {"category": f"{phase.value}_{target}"}
        # Only pass category to get_category, not to list_categories
        elif tool_name == "list_categories":
            args = {}  # list_categories takes no arguments
        return args 