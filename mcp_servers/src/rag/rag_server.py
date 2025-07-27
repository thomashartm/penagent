#!/usr/bin/env python3
"""
RAG MCP Server using FastMCP
Provides RAG knowledge base operations via MCP protocol.
"""

import asyncio
import json
import os
from fastmcp import FastMCP, Context

# Create FastMCP server
mcp = FastMCP("RAG MCP Server")

# Simple in-memory knowledge base for demo
knowledge_base = {
    "pentest_methodologies": [
        "OWASP Top 10",
        "NIST Cybersecurity Framework", 
        "PTES (Penetration Testing Execution Standard)"
    ],
    "common_tools": [
        "nmap - Network discovery and port scanning",
        "metasploit - Exploitation framework",
        "burp suite - Web application security testing",
        "wireshark - Network protocol analyzer"
    ],
    "vulnerability_types": [
        "SQL Injection",
        "Cross-Site Scripting (XSS)",
        "Cross-Site Request Forgery (CSRF)",
        "Insecure Direct Object References (IDOR)"
    ]
}

@mcp.tool
async def search(query: str, max_results: int = 5, ctx: Context = None) -> str:
    """Search the knowledge base for information.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return (default: 5)
    """
    if ctx:
        await ctx.info(f"Searching knowledge base for: {query}")
    
    output = f"RAG search operation: {query}\n"
    
    try:
        # Simple keyword search
        query_lower = query.lower()
        results = []
        
        for category, items in knowledge_base.items():
            for item in items:
                if any(keyword in item.lower() for keyword in query_lower.split()):
                    results.append(f"[{category}] {item}")
        
        if results:
            output += "Knowledge base results:\n"
            for result in results[:max_results]:
                output += f"- {result}\n"
        else:
            output += "No relevant information found in knowledge base.\n"
            
    except Exception as e:
        output += f"[ERROR] Search failed: {str(e)}\n"
    
    return output

@mcp.tool
async def store(category: str, content: str, ctx: Context = None) -> str:
    """Store information in the knowledge base.
    
    Args:
        category: Category to store the information in
        content: Content to store
    """
    if ctx:
        await ctx.info(f"Storing information in category: {category}")
    
    output = f"RAG store operation: {category}\n"
    
    try:
        # Store in knowledge base
        if category not in knowledge_base:
            knowledge_base[category] = []
        
        knowledge_base[category].append(content)
        output += f"Information stored successfully in category '{category}'.\n"
        output += f"Content: {content}\n"
        
    except Exception as e:
        output += f"[ERROR] Store operation failed: {str(e)}\n"
    
    return output

@mcp.tool
async def list_categories(ctx: Context = None) -> str:
    """List all available categories in the knowledge base.
    """
    if ctx:
        await ctx.info("Listing knowledge base categories")
    
    output = "RAG list categories operation\n"
    
    try:
        categories = list(knowledge_base.keys())
        output += f"Available categories ({len(categories)}):\n"
        for category in categories:
            item_count = len(knowledge_base[category])
            output += f"- {category}: {item_count} items\n"
        
    except Exception as e:
        output += f"[ERROR] List categories failed: {str(e)}\n"
    
    return output

@mcp.tool
async def get_category(category: str, ctx: Context = None) -> str:
    """Get all items in a specific category.
    
    Args:
        category: Category name to retrieve
    """
    if ctx:
        await ctx.info(f"Getting category: {category}")
    
    output = f"RAG get category operation: {category}\n"
    
    try:
        if category in knowledge_base:
            items = knowledge_base[category]
            output += f"Category '{category}' contains {len(items)} items:\n"
            for i, item in enumerate(items, 1):
                output += f"{i}. {item}\n"
        else:
            output += f"Category '{category}' not found.\n"
        
    except Exception as e:
        output += f"[ERROR] Get category failed: {str(e)}\n"
    
    return output

@mcp.tool
async def delete_item(category: str, item_index: int, ctx: Context = None) -> str:
    """Delete an item from a category.
    
    Args:
        category: Category name
        item_index: Index of item to delete (1-based)
    """
    if ctx:
        await ctx.info(f"Deleting item {item_index} from category: {category}")
    
    output = f"RAG delete item operation: {category}, item {item_index}\n"
    
    try:
        if category in knowledge_base:
            items = knowledge_base[category]
            if 1 <= item_index <= len(items):
                deleted_item = items.pop(item_index - 1)
                output += f"Successfully deleted item: {deleted_item}\n"
            else:
                output += f"Item index {item_index} out of range (1-{len(items)}).\n"
        else:
            output += f"Category '{category}' not found.\n"
        
    except Exception as e:
        output += f"[ERROR] Delete item failed: {str(e)}\n"
    
    return output

if __name__ == "__main__":
    mcp.run() 