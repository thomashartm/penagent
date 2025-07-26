from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import requests
import json
import time
import os

app = FastAPI(title="ZAP MCP Server", description="MCP server for OWASP ZAP web application security testing")

# ZAP API configuration - use environment variable for Docker networking
ZAP_API_BASE = os.getenv("ZAP_API_BASE", "http://localhost:8090")
ZAP_API_KEY = None  # API key disabled in docker-compose

@app.post('/run')
async def run_tool(request: Request):
    data = await request.json()
    command = data.get('command', '')
    async def event_stream():
        yield f"Running ZAP tool: {command}\n"
        yield f"Using ZAP API at: {ZAP_API_BASE}\n"
        
        try:
            if 'spider' in command.lower():
                # Extract URL from command
                import re
                url_match = re.search(r'https?://[^\s]+', command)
                if url_match:
                    target_url = url_match.group(0)
                    yield f"Starting ZAP spider scan for: {target_url}\n"
                    
                    # Start spider scan
                    spider_url = f"{ZAP_API_BASE}/JSON/spider/action/scan/"
                    params = {'url': target_url}
                    if ZAP_API_KEY:
                        params['apikey'] = ZAP_API_KEY
                    
                    response = requests.post(spider_url, params=params)
                    if response.status_code == 200:
                        scan_id = response.json().get('scan')
                        yield f"Spider scan started with ID: {scan_id}\n"
                        
                        # Wait for scan to complete
                        while True:
                            status_url = f"{ZAP_API_BASE}/JSON/spider/view/status/"
                            params = {'scanId': scan_id}
                            if ZAP_API_KEY:
                                params['apikey'] = ZAP_API_KEY
                            
                            status_response = requests.get(status_url, params=params)
                            if status_response.status_code == 200:
                                status = status_response.json().get('status')
                                yield f"Spider status: {status}\n"
                                
                                if status == '100':
                                    yield "Spider scan completed!\n"
                                    break
                            
                            await asyncio.sleep(2)
                    else:
                        yield f"Failed to start spider scan: {response.text}\n"
                else:
                    yield "[ERROR] No URL found in spider command\n"
                    
            elif 'active' in command.lower() or 'scan' in command.lower():
                # Extract URL from command
                import re
                url_match = re.search(r'https?://[^\s]+', command)
                if url_match:
                    target_url = url_match.group(0)
                    yield f"Starting ZAP active scan for: {target_url}\n"
                    
                    # Start active scan
                    scan_url = f"{ZAP_API_BASE}/JSON/ascan/action/scan/"
                    params = {'url': target_url}
                    if ZAP_API_KEY:
                        params['apikey'] = ZAP_API_KEY
                    
                    response = requests.post(scan_url, params=params)
                    if response.status_code == 200:
                        scan_id = response.json().get('scan')
                        yield f"Active scan started with ID: {scan_id}\n"
                        
                        # Wait for scan to complete
                        while True:
                            status_url = f"{ZAP_API_BASE}/JSON/ascan/view/status/"
                            params = {'scanId': scan_id}
                            if ZAP_API_KEY:
                                params['apikey'] = ZAP_API_KEY
                            
                            status_response = requests.get(status_url, params=params)
                            if status_response.status_code == 200:
                                status = status_response.json().get('status')
                                yield f"Active scan status: {status}%\n"
                                
                                if status == '100':
                                    yield "Active scan completed!\n"
                                    break
                            
                            await asyncio.sleep(5)
                    else:
                        yield f"Failed to start active scan: {response.text}\n"
                else:
                    yield "[ERROR] No URL found in scan command\n"
                    
            elif 'alerts' in command.lower():
                # Get alerts
                alerts_url = f"{ZAP_API_BASE}/JSON/core/view/alerts/"
                params = {}
                if ZAP_API_KEY:
                    params['apikey'] = ZAP_API_KEY
                
                response = requests.get(alerts_url, params=params)
                if response.status_code == 200:
                    alerts = response.json().get('alerts', [])
                    yield f"Found {len(alerts)} alerts:\n"
                    for alert in alerts[:10]:  # Limit to 10 alerts
                        yield f"- {alert.get('risk')}: {alert.get('name')} at {alert.get('url')}\n"
                else:
                    yield f"Failed to get alerts: {response.text}\n"
                    
            else:
                yield f"Available ZAP commands: spider <url>, active scan <url>, alerts\n"
                yield f"Command received: {command}\n"
                
        except Exception as e:
            yield f"[ERROR] ZAP operation failed: {str(e)}\n"
            
    return StreamingResponse(event_stream(), media_type='text/plain')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005) 