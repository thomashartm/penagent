#!/usr/bin/env python3
"""
Kali Linux MCP Server using FastMCP (minimal, correct pattern)
Provides access to Kali Linux pentesting tools via MCP protocol.
"""

from fastmcp import FastMCP
import subprocess

# Create FastMCP server
mcp = FastMCP("Kali Linux MCP Server")

@mcp.tool
def nmap(target: str, options: str = "-sV -sC") -> str:
    """Network discovery and security auditing tool.
    Args:
        target: Target host or network (e.g., 192.168.1.1, 192.168.1.0/24)
        options: Nmap options (default: -sV -sC)
    """
    command = ["nmap"] + options.split() + [target]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        output = f"Command: {' '.join(command)}\n"
        output += f"Exit Code: {result.returncode}\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out: {' '.join(command)}"
    except Exception as e:
        return f"Execution error: {str(e)}"

@mcp.tool
def gobuster(url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt", extensions: str = None) -> str:
    """Directory/file enumeration tool.
    Args:
        url: Target URL (e.g., https://example.com)
        wordlist: Wordlist path (default: /usr/share/wordlists/dirb/common.txt)
        extensions: File extensions to search (e.g., php,html,txt)
    """
    command = ["gobuster", "dir", "-u", url, "-w", wordlist]
    if extensions:
        command += ["-x", extensions]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        output = f"Command: {' '.join(command)}\n"
        output += f"Exit Code: {result.returncode}\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out: {' '.join(command)}"
    except Exception as e:
        return f"Execution error: {str(e)}"

@mcp.tool
def hydra(target: str, service: str, username: str = "admin", password: str = "/usr/share/wordlists/rockyou.txt") -> str:
    """Password cracking tool.
    Args:
        target: Target host
        service: Service to attack (e.g., ssh, ftp, http-post-form)
        username: Username or user list
        password: Password or password list
    """
    command = ["hydra", "-L", username, "-P", password, target, service]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        output = f"Command: {' '.join(command)}\n"
        output += f"Exit Code: {result.returncode}\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out: {' '.join(command)}"
    except Exception as e:
        return f"Execution error: {str(e)}"

@mcp.tool
def nikto(url: str, options: str = "-h") -> str:
    """Web server scanner.
    Args:
        url: Target URL (e.g., https://example.com)
        options: Additional Nikto options (default: -h)
    """
    command = ["nikto"] + options.split() + [url]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        output = f"Command: {' '.join(command)}\n"
        output += f"Exit Code: {result.returncode}\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out: {' '.join(command)}"
    except Exception as e:
        return f"Execution error: {str(e)}"

@mcp.tool
def metasploit(command: str) -> str:
    """Metasploit Framework command execution.
    Args:
        command: Metasploit command (e.g., msfconsole -q -x 'use exploit/multi/handler; set PAYLOAD windows/meterpreter/reverse_tcp; set LHOST 192.168.1.100; set LPORT 4444; exploit')
    """
    # Wrap in msfconsole if not already
    if not command.strip().startswith("msfconsole"):
        command = f"msfconsole -q -x '{command}'"
    command_list = ["bash", "-c", command]
    try:
        result = subprocess.run(command_list, capture_output=True, text=True, timeout=300)
        output = f"Command: {' '.join(command_list)}\n"
        output += f"Exit Code: {result.returncode}\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out: {' '.join(command_list)}"
    except Exception as e:
        return f"Execution error: {str(e)}"

@mcp.tool
def shell_command(command: str) -> str:
    """Execute arbitrary shell command in Kali container.
    Args:
        command: Shell command to execute
    """
    command_list = ["bash", "-c", command]
    try:
        result = subprocess.run(command_list, capture_output=True, text=True, timeout=300)
        output = f"Command: {' '.join(command_list)}\n"
        output += f"Exit Code: {result.returncode}\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out: {' '.join(command_list)}"
    except Exception as e:
        return f"Execution error: {str(e)}"

@mcp.tool
def recon_ng(command: str) -> str:
    """Run a recon-ng command.
    Args:
        command: Recon-ng command to execute (e.g., 'modules load recon/domains-hosts/google_site_web; run')
    """
    # recon-ng is usually run in interactive mode, but you can pass commands via -c
    cmd = ["recon-ng", "-c", command]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = f"Command: {' '.join(cmd)}\n"
        output += f"Exit Code: {result.returncode}\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out: {' '.join(cmd)}"
    except Exception as e:
        return f"Execution error: {str(e)}"

@mcp.tool
def google_dork(query: str) -> str:
    """Perform a Google dorking search using curl.
    Args:
        query: Google dork query (e.g., 'site:example.com inurl:admin')
    """
    # Use curl to fetch Google search results (note: may be blocked by Google)
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    cmd = ["curl", "-A", "Mozilla/5.0", "-L", search_url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = f"Command: {' '.join(cmd)}\n"
        output += f"Exit Code: {result.returncode}\n"
        output += f"STDOUT (truncated):\n{result.stdout[:2000]}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out: {' '.join(cmd)}"
    except Exception as e:
        return f"Execution error: {str(e)}"

@mcp.tool
def nuclei(target: str, template: str = None) -> str:
    """Run nuclei vulnerability scanner.
    Args:
        target: Target URL or IP
        template: Optional nuclei template (e.g., 'cves', 'vulnerabilities')
    """
    command = ["nuclei", "-u", target]
    if template:
        command += ["-t", template]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        output = f"Command: {' '.join(command)}\n"
        output += f"Exit Code: {result.returncode}\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out: {' '.join(command)}"
    except Exception as e:
        return f"Execution error: {str(e)}"

@mcp.tool
def sublist3r(domain: str) -> str:
    """Run Sublist3r for subdomain enumeration.
    Args:
        domain: Target domain (e.g., 'example.com')
    """
    command = ["sublist3r", "-d", domain]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        output = f"Command: {' '.join(command)}\n"
        output += f"Exit Code: {result.returncode}\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out: {' '.join(command)}"
    except Exception as e:
        return f"Execution error: {str(e)}"

@mcp.tool
def whatweb(target: str, args: str = None) -> str:
    """Run WhatWeb web scanner.
    Args:
        target: Target URL or IP
        args: Optional additional WhatWeb arguments (e.g., '-v')
    """
    command = ["whatweb", target]
    if args:
        command += args.split()
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        output = f"Command: {' '.join(command)}\n"
        output += f"Exit Code: {result.returncode}\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out: {' '.join(command)}"
    except Exception as e:
        return f"Execution error: {str(e)}"

if __name__ == "__main__":
    mcp.run() 