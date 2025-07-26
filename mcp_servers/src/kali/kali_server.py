from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import subprocess

app = FastAPI(title="Kali MCP Server", description="MCP server for Kali Linux pentesting tools")

@app.post('/run')
async def run_tool(request: Request):
    data = await request.json()
    command = data.get('command', '')
    async def event_stream():
        yield f"Running Kali tool: {command}\n"
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            yield line.decode()
        err = await proc.stderr.read()
        if err:
            yield f"[stderr] {err.decode()}"
        await proc.wait()
        yield f"[exit code] {proc.returncode}\n"
    return StreamingResponse(event_stream(), media_type='text/plain')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 