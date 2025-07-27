#!/usr/bin/env python3
"""
Kali Linux MCP Server using FastMCP
Provides access to Kali Linux pentesting tools via MCP protocol.
"""

import asyncio
import subprocess
from fastmcp import FastMCP, Context

# Create FastMCP server
mcp = FastMCP("Kali Linux MCP Server")

@mcp.tool
async def nmap(target: str, options: str = "-sV -sC", ctx: Context = None) -> str:
    """Network discovery and security auditing tool.
    
    Args:
        target: Target host or network (e.g., 192.168.1.1, 192.168.1.0/24)
        options: Nmap options (default: -sV -sC)
    """
    if ctx:
        await ctx.info(f"Running nmap {options} {target}")
    
    try:
        command = f"nmap {options} {target}"
        process = await asyncio.create_subprocess_exec(
            "docker", "exec", "mcp-kali", "/bin/bash", "-c", command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
        
        output = f"Command: {command}\n"
        output += f"Exit Code: {process.returncode}\n"
        output += f"STDOUT:\n{stdout.decode('utf-8', errors='ignore')}\n"
        
        if stderr:
            output += f"STDERR:\n{stderr.decode('utf-8', errors='ignore')}\n"
        
        return output
        
    except asyncio.TimeoutError:
        return f"Command timed out: {command}"
    except Exception as e:
        return f"Execution error: {str(e)}"

@mcp.tool
async def gobuster(url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt", extensions: str = None, ctx: Context = None) -> str:
    """Directory/file enumeration tool.
    
    Args:
        url: Target URL (e.g., https://example.com)
        wordlist: Wordlist path (default: /usr/share/wordlists/dirb/common.txt)
        extensions: File extensions to search (e.g., php,html,txt)
    """
    if ctx:
        await ctx.info(f"Running gobuster dir -u {url} -w {wordlist}")
    
    try:
        command = f"gobuster dir -u {url} -w {wordlist}"
        if extensions:
            command += f" -x {extensions}"
        
        process = await asyncio.create_subprocess_exec(
            "docker", "exec", "mcp-kali", "/bin/bash", "-c", command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
        
        output = f"Command: {command}\n"
        output += f"Exit Code: {process.returncode}\n"
        output += f"STDOUT:\n{stdout.decode('utf-8', errors='ignore')}\n"
        
        if stderr:
            output += f"STDERR:\n{stderr.decode('utf-8', errors='ignore')}\n"
        
        return output
        
    except asyncio.TimeoutError:
        return f"Command timed out: {command}"
    except Exception as e:
        return f"Execution error: {str(e)}"

@mcp.tool
async def hydra(target: str, service: str, username: str = "admin", password: str = "/usr/share/wordlists/rockyou.txt", ctx: Context = None) -> str:
    """Password cracking tool.
    
    Args:
        target: Target host
        service: Service to attack (e.g., ssh, ftp, http-post-form)
        username: Username or user list
        password: Password or password list
    """
    if ctx:
        await ctx.info(f"Running hydra -L {username} -P {password} {target} {service}")
    
    try:
        command = f"hydra -L {username} -P {password} {target} {service}"
        
        process = await asyncio.create_subprocess_exec(
            "docker", "exec", "mcp-kali", "/bin/bash", "-c", command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
        
        output = f"Command: {command}\n"
        output += f"Exit Code: {process.returncode}\n"
        output += f"STDOUT:\n{stdout.decode('utf-8', errors='ignore')}\n"
        
        if stderr:
            output += f"STDERR:\n{stderr.decode('utf-8', errors='ignore')}\n"
        
        return output
        
    except asyncio.TimeoutError:
        return f"Command timed out: {command}"
    except Exception as e:
        return f"Execution error: {str(e)}"

@mcp.tool
async def nikto(url: str, options: str = "-h", ctx: Context = None) -> str:
    """Web server scanner.
    
    Args:
        url: Target URL (e.g., https://example.com)
        options: Additional Nikto options (default: -h)
    """
    if ctx:
        await ctx.info(f"Running nikto {options} {url}")
    
    try:
        command = f"nikto {options} {url}"
        
        process = await asyncio.create_subprocess_exec(
            "docker", "exec", "mcp-kali", "/bin/bash", "-c", command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
        
        output = f"Command: {command}\n"
        output += f"Exit Code: {process.returncode}\n"
        output += f"STDOUT:\n{stdout.decode('utf-8', errors='ignore')}\n"
        
        if stderr:
            output += f"STDERR:\n{stderr.decode('utf-8', errors='ignore')}\n"
        
        return output
        
    except asyncio.TimeoutError:
        return f"Command timed out: {command}"
    except Exception as e:
        return f"Execution error: {str(e)}"

@mcp.tool
async def metasploit(command: str, ctx: Context = None) -> str:
    """Metasploit Framework command execution.
    
    Args:
        command: Metasploit command (e.g., msfconsole -q -x 'use exploit/multi/handler; set PAYLOAD windows/meterpreter/reverse_tcp; set LHOST 192.168.1.100; set LPORT 4444; exploit')
    """
    if ctx:
        await ctx.info(f"Running metasploit command: {command}")
    
    try:
        # Wrap in msfconsole if not already
        if not command.startswith("msfconsole"):
            command = f"msfconsole -q -x '{command}'"
        
        process = await asyncio.create_subprocess_exec(
            "docker", "exec", "mcp-kali", "/bin/bash", "-c", command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
        
        output = f"Command: {command}\n"
        output += f"Exit Code: {process.returncode}\n"
        output += f"STDOUT:\n{stdout.decode('utf-8', errors='ignore')}\n"
        
        if stderr:
            output += f"STDERR:\n{stderr.decode('utf-8', errors='ignore')}\n"
        
        return output
        
    except asyncio.TimeoutError:
        return f"Command timed out: {command}"
    except Exception as e:
        return f"Execution error: {str(e)}"

@mcp.tool
async def shell_command(command: str, ctx: Context = None) -> str:
    """Execute arbitrary shell command in Kali container.
    
    Args:
        command: Shell command to execute
    """
    if ctx:
        await ctx.info(f"Running shell command: {command}")
    
    try:
        process = await asyncio.create_subprocess_exec(
            "docker", "exec", "mcp-kali", "/bin/bash", "-c", command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
        
        output = f"Command: {command}\n"
        output += f"Exit Code: {process.returncode}\n"
        output += f"STDOUT:\n{stdout.decode('utf-8', errors='ignore')}\n"
        
        if stderr:
            output += f"STDERR:\n{stderr.decode('utf-8', errors='ignore')}\n"
        
        return output
        
    except asyncio.TimeoutError:
        return f"Command timed out: {command}"
    except Exception as e:
        return f"Execution error: {str(e)}"

if __name__ == "__main__":
    mcp.run() 