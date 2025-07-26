from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import requests
from urllib.parse import urljoin, urlparse
import re

app = FastAPI(title="OWASP MCP Server", description="MCP server for OWASP web application security testing")

@app.post('/run')
async def run_tool(request: Request):
    data = await request.json()
    command = data.get('command', '')
    async def event_stream():
        yield f"Running OWASP tool: {command}\n"
        
        if 'spider' in command.lower():
            # Extract URL from command
            url_match = re.search(r'https?://[^\s]+', command)
            if url_match:
                target_url = url_match.group(0)
                yield f"Spidering: {target_url}\n"
                try:
                    # Simple spider implementation
                    visited = set()
                    to_visit = [target_url]
                    
                    while to_visit and len(visited) < 10:  # Limit to 10 URLs
                        current_url = to_visit.pop(0)
                        if current_url in visited:
                            continue
                            
                        visited.add(current_url)
                        yield f"Visiting: {current_url}\n"
                        
                        try:
                            response = requests.get(current_url, timeout=10)
                            if response.status_code == 200:
                                # Find links
                                links = re.findall(r'href=["\']([^"\']+)["\']', response.text)
                                for link in links:
                                    full_url = urljoin(current_url, link)
                                    if full_url.startswith(target_url) and full_url not in visited:
                                        to_visit.append(full_url)
                        except Exception as e:
                            yield f"Error visiting {current_url}: {str(e)}\n"
                            
                    yield f"Spidering complete. Found {len(visited)} URLs.\n"
                    
                except Exception as e:
                    yield f"[ERROR] Spidering failed: {str(e)}\n"
            else:
                yield "[ERROR] No URL found in spider command\n"
        else:
            yield f"OWASP command executed: {command}\n"
            
    return StreamingResponse(event_stream(), media_type='text/plain')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003) 