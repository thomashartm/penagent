#!/usr/bin/env python3
"""
WebSearch MCP Server using FastMCP
Provides web search functionality via MCP protocol.
"""

import asyncio
import requests
from bs4 import BeautifulSoup
from fastmcp import FastMCP, Context

# Create FastMCP server
mcp = FastMCP("WebSearch MCP Server")

@mcp.tool
async def search(query: str, max_results: int = 5, ctx: Context = None) -> str:
    """Search the web for information.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return (default: 5)
    """
    if ctx:
        await ctx.info(f"Searching web for: {query}")
    
    output = f"Searching web for: {query}\n"
    
    try:
        # Use DuckDuckGo for search
        search_url = f"https://duckduckgo.com/html/?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Extract search results
        for result in soup.find_all('a', class_='result__a')[:max_results]:
            title = result.get_text(strip=True)
            url = result.get('href', '')
            if title and url:
                results.append(f"- {title}: {url}")
        
        if results:
            output += "Search results:\n"
            for result in results:
                output += result + "\n"
        else:
            output += "No results found.\n"
            
    except Exception as e:
        output += f"[ERROR] Search failed: {str(e)}\n"
    
    return output

@mcp.tool
async def search_news(query: str, max_results: int = 5, ctx: Context = None) -> str:
    """Search for news articles.
    
    Args:
        query: News search query
        max_results: Maximum number of results to return (default: 5)
    """
    if ctx:
        await ctx.info(f"Searching news for: {query}")
    
    output = f"Searching news for: {query}\n"
    
    try:
        # Use DuckDuckGo news search
        search_url = f"https://duckduckgo.com/html/?q={query}+news"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Extract news results
        for result in soup.find_all('a', class_='result__a')[:max_results]:
            title = result.get_text(strip=True)
            url = result.get('href', '')
            if title and url:
                results.append(f"- {title}: {url}")
        
        if results:
            output += "News results:\n"
            for result in results:
                output += result + "\n"
        else:
            output += "No news results found.\n"
            
    except Exception as e:
        output += f"[ERROR] News search failed: {str(e)}\n"
    
    return output

@mcp.tool
async def search_images(query: str, max_results: int = 5, ctx: Context = None) -> str:
    """Search for images.
    
    Args:
        query: Image search query
        max_results: Maximum number of results to return (default: 5)
    """
    if ctx:
        await ctx.info(f"Searching images for: {query}")
    
    output = f"Searching images for: {query}\n"
    
    try:
        # Use DuckDuckGo image search
        search_url = f"https://duckduckgo.com/html/?q={query}&iax=images&ia=images"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Extract image results
        for result in soup.find_all('a', class_='result__a')[:max_results]:
            title = result.get_text(strip=True)
            url = result.get('href', '')
            if title and url:
                results.append(f"- {title}: {url}")
        
        if results:
            output += "Image results:\n"
            for result in results:
                output += result + "\n"
        else:
            output += "No image results found.\n"
            
    except Exception as e:
        output += f"[ERROR] Image search failed: {str(e)}\n"
    
    return output

if __name__ == "__main__":
    mcp.run()
    import time
    while True:
        time.sleep(60) 