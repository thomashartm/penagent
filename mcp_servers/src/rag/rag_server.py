from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
import os

app = FastAPI(title="RAG MCP Server", description="MCP server for RAG knowledge base operations")

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

@app.post('/run')
async def run_tool(request: Request):
    data = await request.json()
    command = data.get('command', '')
    async def event_stream():
        yield f"RAG operation: {command}\n"
        
        if 'search' in command.lower() or 'query' in command.lower():
            # Simple keyword search
            query = command.lower()
            results = []
            
            for category, items in knowledge_base.items():
                for item in items:
                    if any(keyword in item.lower() for keyword in query.split()):
                        results.append(f"[{category}] {item}")
            
            if results:
                yield "Knowledge base results:\n"
                for result in results[:5]:  # Limit to 5 results
                    yield f"- {result}\n"
            else:
                yield "No relevant information found in knowledge base.\n"
                
        elif 'store' in command.lower() or 'add' in command.lower():
            # Simple storage operation
            yield "Storing information in knowledge base...\n"
            # In a real implementation, this would store to a vector database
            yield "Information stored successfully.\n"
            
        else:
            yield f"Available RAG operations: search, store\n"
            yield f"Command received: {command}\n"
            
    return StreamingResponse(event_stream(), media_type='text/plain')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 