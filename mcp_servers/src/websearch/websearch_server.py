from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="WebSearch MCP Server", description="MCP server for web search functionality")

@app.post('/run')
async def run_tool(request: Request):
    data = await request.json()
    query = data.get('command', '')
    async def event_stream():
        yield f"Searching web for: {query}\n"
        try:
            # Use DuckDuckGo for search
            search_url = f"https://duckduckgo.com/html/?q={query}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Extract search results
            for result in soup.find_all('a', class_='result__a')[:5]:
                title = result.get_text(strip=True)
                url = result.get('href', '')
                if title and url:
                    results.append(f"- {title}: {url}")
            
            if results:
                yield "Search results:\n"
                for result in results:
                    yield result + "\n"
            else:
                yield "No results found.\n"
                
        except Exception as e:
            yield f"[ERROR] Search failed: {str(e)}\n"
            
    return StreamingResponse(event_stream(), media_type='text/plain')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 