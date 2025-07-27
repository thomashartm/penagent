#!/usr/bin/env python3
"""
OWASP MCP Server using FastMCP
Provides OWASP web application security testing tools via MCP protocol.
"""

import asyncio
import requests
from urllib.parse import urljoin, urlparse
import re
from fastmcp import FastMCP, Context

# Create FastMCP server
mcp = FastMCP("OWASP MCP Server")

@mcp.tool
async def spider(url: str, max_urls: int = 10, ctx: Context = None) -> str:
    """Spider/crawl a website to discover URLs.
    
    Args:
        url: Target URL to spider (e.g., https://example.com)
        max_urls: Maximum number of URLs to discover (default: 10)
    """
    if ctx:
        await ctx.info(f"Spidering website: {url}")
    
    output = f"OWASP spider operation: {url}\n"
    
    try:
        # Simple spider implementation
        visited = set()
        to_visit = [url]
        
        while to_visit and len(visited) < max_urls:
            current_url = to_visit.pop(0)
            if current_url in visited:
                continue
                
            visited.add(current_url)
            output += f"Visiting: {current_url}\n"
            
            try:
                response = requests.get(current_url, timeout=10)
                if response.status_code == 200:
                    # Find links
                    links = re.findall(r'href=["\']([^"\']+)["\']', response.text)
                    for link in links:
                        full_url = urljoin(current_url, link)
                        if full_url.startswith(url) and full_url not in visited:
                            to_visit.append(full_url)
            except Exception as e:
                output += f"Error visiting {current_url}: {str(e)}\n"
                
        output += f"Spidering complete. Found {len(visited)} URLs.\n"
        
    except Exception as e:
        output += f"[ERROR] Spidering failed: {str(e)}\n"
    
    return output

@mcp.tool
async def check_headers(url: str, ctx: Context = None) -> str:
    """Check security headers of a website.
    
    Args:
        url: Target URL to check headers
    """
    if ctx:
        await ctx.info(f"Checking security headers for: {url}")
    
    output = f"OWASP security headers check: {url}\n"
    
    try:
        response = requests.get(url, timeout=10)
        
        security_headers = {
            'X-Frame-Options': 'Prevents clickjacking',
            'X-Content-Type-Options': 'Prevents MIME type sniffing',
            'X-XSS-Protection': 'XSS protection',
            'Strict-Transport-Security': 'Enforces HTTPS',
            'Content-Security-Policy': 'Content Security Policy',
            'Referrer-Policy': 'Referrer policy',
            'Permissions-Policy': 'Permissions policy'
        }
        
        output += "Security headers analysis:\n"
        for header, description in security_headers.items():
            value = response.headers.get(header)
            if value:
                output += f"✅ {header}: {value} - {description}\n"
            else:
                output += f"❌ {header}: Missing - {description}\n"
        
    except Exception as e:
        output += f"[ERROR] Header check failed: {str(e)}\n"
    
    return output

@mcp.tool
async def check_ssl(url: str, ctx: Context = None) -> str:
    """Check SSL/TLS configuration of a website.
    
    Args:
        url: Target URL to check SSL
    """
    if ctx:
        await ctx.info(f"Checking SSL configuration for: {url}")
    
    output = f"OWASP SSL check: {url}\n"
    
    try:
        # Ensure HTTPS
        if not url.startswith('https://'):
            url = url.replace('http://', 'https://')
        
        response = requests.get(url, timeout=10)
        
        output += "SSL/TLS analysis:\n"
        
        # Check if HTTPS is used
        if response.url.startswith('https://'):
            output += "✅ HTTPS is being used\n"
        else:
            output += "❌ HTTPS is not being used\n"
        
        # Check certificate info
        if hasattr(response, 'raw') and hasattr(response.raw, 'connection'):
            cert = response.raw.connection.sock.getpeercert()
            if cert:
                output += f"✅ Certificate found\n"
                output += f"   Subject: {cert.get('subject', 'N/A')}\n"
                output += f"   Issuer: {cert.get('issuer', 'N/A')}\n"
                output += f"   Expires: {cert.get('notAfter', 'N/A')}\n"
        
    except Exception as e:
        output += f"[ERROR] SSL check failed: {str(e)}\n"
    
    return output

@mcp.tool
async def check_open_redirects(url: str, ctx: Context = None) -> str:
    """Check for open redirect vulnerabilities.
    
    Args:
        url: Target URL to check for open redirects
    """
    if ctx:
        await ctx.info(f"Checking for open redirects: {url}")
    
    output = f"OWASP open redirect check: {url}\n"
    
    try:
        # Common redirect parameters
        redirect_params = ['redirect', 'url', 'next', 'target', 'redir', 'destination', 'return', 'returnTo']
        
        output += "Testing common redirect parameters:\n"
        
        for param in redirect_params:
            test_url = f"{url}?{param}=https://evil.com"
            try:
                response = requests.get(test_url, timeout=5, allow_redirects=False)
                if response.status_code in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location', '')
                    if 'evil.com' in location:
                        output += f"❌ Potential open redirect found: {param}\n"
                    else:
                        output += f"✅ {param}: Redirects to {location}\n"
                else:
                    output += f"✅ {param}: No redirect\n"
            except:
                output += f"⚠️ {param}: Error testing\n"
        
    except Exception as e:
        output += f"[ERROR] Open redirect check failed: {str(e)}\n"
    
    return output

@mcp.tool
async def check_sql_injection(url: str, ctx: Context = None) -> str:
    """Check for SQL injection vulnerabilities.
    
    Args:
        url: Target URL to check for SQL injection
    """
    if ctx:
        await ctx.info(f"Checking for SQL injection: {url}")
    
    output = f"OWASP SQL injection check: {url}\n"
    
    try:
        # Common SQL injection payloads
        payloads = [
            "' OR '1'='1",
            "' UNION SELECT NULL--",
            "'; DROP TABLE users--",
            "' OR 1=1--"
        ]
        
        output += "Testing common SQL injection payloads:\n"
        
        for payload in payloads:
            test_url = f"{url}?id={payload}"
            try:
                response = requests.get(test_url, timeout=5)
                
                # Check for common SQL error messages
                error_indicators = [
                    'sql syntax',
                    'mysql_fetch',
                    'oracle error',
                    'sql server',
                    'postgresql',
                    'sqlite'
                ]
                
                found_error = False
                for indicator in error_indicators:
                    if indicator.lower() in response.text.lower():
                        output += f"❌ Potential SQL injection: {payload}\n"
                        found_error = True
                        break
                
                if not found_error:
                    output += f"✅ {payload}: No obvious SQL errors\n"
                    
            except:
                output += f"⚠️ {payload}: Error testing\n"
        
    except Exception as e:
        output += f"[ERROR] SQL injection check failed: {str(e)}\n"
    
    return output

if __name__ == "__main__":
    mcp.run() 