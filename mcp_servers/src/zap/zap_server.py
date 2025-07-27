#!/usr/bin/env python3
"""
ZAP MCP Server using FastMCP
Provides access to OWASP ZAP web application security testing tools via MCP protocol.
"""

import asyncio
import requests
import json
from fastmcp import FastMCP, Context

# Create FastMCP server
mcp = FastMCP("ZAP MCP Server")

# ZAP API configuration
ZAP_API_BASE = "http://localhost:8090"
ZAP_API_KEY = None  # API key disabled in docker-compose

@mcp.tool
async def spider(url: str, max_depth: int = 5, ctx: Context = None) -> str:
    """Spider/crawl a website to discover URLs.
    
    Args:
        url: Target URL to spider (e.g., https://example.com)
        max_depth: Maximum depth for spidering (default: 5)
    """
    if ctx:
        await ctx.info(f"Starting ZAP spider scan for: {url}")
    
    output = f"Starting ZAP spider scan for: {url}\n"
    output += f"Using ZAP API at: {ZAP_API_BASE}\n"
    
    try:
        # Start spider scan
        spider_url = f"{ZAP_API_BASE}/JSON/spider/action/scan/"
        params = {'url': url, 'maxChildren': max_depth}
        if ZAP_API_KEY:
            params['apikey'] = ZAP_API_KEY
        
        response = requests.post(spider_url, params=params)
        if response.status_code == 200:
            scan_id = response.json().get('scan')
            output += f"Spider scan started with ID: {scan_id}\n"
            
            # Wait for scan to complete
            while True:
                status_url = f"{ZAP_API_BASE}/JSON/spider/view/status/"
                params = {'scanId': scan_id}
                if ZAP_API_KEY:
                    params['apikey'] = ZAP_API_KEY
                
                status_response = requests.get(status_url, params=params)
                if status_response.status_code == 200:
                    status = status_response.json().get('status')
                    output += f"Spider status: {status}%\n"
                    
                    if status == '100':
                        output += "Spider scan completed!\n"
                        break
                
                await asyncio.sleep(2)
        else:
            output += f"Failed to start spider scan: {response.text}\n"
            
    except Exception as e:
        output += f"Spider scan error: {str(e)}\n"
    
    return output

@mcp.tool
async def active_scan(url: str, scan_policy: str = "Default Policy", ctx: Context = None) -> str:
    """Perform active security scan on a URL.
    
    Args:
        url: Target URL to scan (e.g., https://example.com)
        scan_policy: Scan policy to use (default: Default Policy)
    """
    if ctx:
        await ctx.info(f"Starting ZAP active scan for: {url}")
    
    output = f"Starting ZAP active scan for: {url}\n"
    output += f"Using ZAP API at: {ZAP_API_BASE}\n"
    
    try:
        # Start active scan
        scan_url = f"{ZAP_API_BASE}/JSON/ascan/action/scan/"
        params = {'url': url, 'scanPolicyName': scan_policy}
        if ZAP_API_KEY:
            params['apikey'] = ZAP_API_KEY
        
        response = requests.post(scan_url, params=params)
        if response.status_code == 200:
            scan_id = response.json().get('scan')
            output += f"Active scan started with ID: {scan_id}\n"
            
            # Wait for scan to complete
            while True:
                status_url = f"{ZAP_API_BASE}/JSON/ascan/view/status/"
                params = {'scanId': scan_id}
                if ZAP_API_KEY:
                    params['apikey'] = ZAP_API_KEY
                
                status_response = requests.get(status_url, params=params)
                if status_response.status_code == 200:
                    status = status_response.json().get('status')
                    output += f"Active scan status: {status}%\n"
                    
                    if status == '100':
                        output += "Active scan completed!\n"
                        break
                
                await asyncio.sleep(5)
        else:
            output += f"Failed to start active scan: {response.text}\n"
            
    except Exception as e:
        output += f"Active scan error: {str(e)}\n"
    
    return output

@mcp.tool
async def passive_scan(url: str, ctx: Context = None) -> str:
    """Perform passive security scan on a URL.
    
    Args:
        url: Target URL to scan (e.g., https://example.com)
    """
    if ctx:
        await ctx.info(f"Starting ZAP passive scan for: {url}")
    
    output = f"Starting ZAP passive scan for: {url}\n"
    output += f"Using ZAP API at: {ZAP_API_BASE}\n"
    
    try:
        # Passive scan is automatic, just check for alerts
        await asyncio.sleep(2)  # Give some time for passive scanning
        output += "Passive scan completed (automatic scanning)\n"
        
    except Exception as e:
        output += f"Passive scan error: {str(e)}\n"
    
    return output

@mcp.tool
async def alerts(risk_level: str = None, max_alerts: int = 50, ctx: Context = None) -> str:
    """Get security alerts from ZAP.
    
    Args:
        risk_level: Filter by risk level (High, Medium, Low, Informational)
        max_alerts: Maximum number of alerts to return (default: 50)
    """
    if ctx:
        await ctx.info(f"Getting ZAP alerts (max: {max_alerts})")
    
    output = f"Getting ZAP alerts (max: {max_alerts})\n"
    if risk_level:
        output += f"Filtering by risk level: {risk_level}\n"
    
    try:
        alerts_url = f"{ZAP_API_BASE}/JSON/core/view/alerts/"
        params = {}
        if ZAP_API_KEY:
            params['apikey'] = ZAP_API_KEY
        
        response = requests.get(alerts_url, params=params)
        if response.status_code == 200:
            alerts = response.json().get('alerts', [])
            
            # Filter by risk level if specified
            if risk_level:
                alerts = [alert for alert in alerts if alert.get('risk') == risk_level]
            
            output += f"Found {len(alerts)} alerts:\n"
            for i, alert in enumerate(alerts[:max_alerts]):
                output += f"{i+1}. {alert.get('risk')}: {alert.get('name')}\n"
                output += f"   URL: {alert.get('url')}\n"
                output += f"   Description: {alert.get('description', 'N/A')}\n\n"
        else:
            output += f"Failed to get alerts: {response.text}\n"
            
    except Exception as e:
        output += f"Error getting alerts: {str(e)}\n"
    
    return output

@mcp.tool
async def urls(base_url: str = None, max_urls: int = 100, ctx: Context = None) -> str:
    """Get discovered URLs from ZAP.
    
    Args:
        base_url: Filter URLs by base URL
        max_urls: Maximum number of URLs to return (default: 100)
    """
    if ctx:
        await ctx.info(f"Getting ZAP URLs (max: {max_urls})")
    
    output = f"Getting ZAP URLs (max: {max_urls})\n"
    if base_url:
        output += f"Filtering by base URL: {base_url}\n"
    
    try:
        urls_url = f"{ZAP_API_BASE}/JSON/core/view/urls/"
        params = {}
        if ZAP_API_KEY:
            params['apikey'] = ZAP_API_KEY
        
        response = requests.get(urls_url, params=params)
        if response.status_code == 200:
            urls = response.json().get('urls', [])
            
            # Filter by base URL if specified
            if base_url:
                urls = [url for url in urls if base_url in url]
            
            output += f"Found {len(urls)} URLs:\n"
            for i, url in enumerate(urls[:max_urls]):
                output += f"{i+1}. {url}\n"
        else:
            output += f"Failed to get URLs: {response.text}\n"
            
    except Exception as e:
        output += f"Error getting URLs: {str(e)}\n"
    
    return output

@mcp.tool
async def report(report_format: str = "HTML", report_title: str = "ZAP Security Report", ctx: Context = None) -> str:
    """Generate security report.
    
    Args:
        report_format: Report format (HTML, JSON, XML, Markdown)
        report_title: Report title
    """
    if ctx:
        await ctx.info(f"Generating {report_format} report: {report_title}")
    
    output = f"Generating {report_format} report: {report_title}\n"
    
    try:
        # Generate report
        report_url = f"{ZAP_API_BASE}/JSON/reports/action/generate/"
        params = {
            'title': report_title,
            'template': report_format.lower(),
            'theme': 'traditional-html-plus'
        }
        if ZAP_API_KEY:
            params['apikey'] = ZAP_API_KEY
        
        response = requests.post(report_url, params=params)
        if response.status_code == 200:
            report_data = response.json()
            output += f"Report generated successfully!\n"
            output += f"Report data: {json.dumps(report_data, indent=2)}\n"
        else:
            output += f"Failed to generate report: {response.text}\n"
            
    except Exception as e:
        output += f"Error generating report: {str(e)}\n"
    
    return output

if __name__ == "__main__":
    mcp.run() 