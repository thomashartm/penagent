import requests

class MCPClientNode:
    def __init__(self, output_dir, job_id, mcp_servers=None):
        self.output_dir = output_dir
        self.job_id = job_id
        # mcp_servers: dict mapping tool name to URL
        self.mcp_servers = mcp_servers or {
            'kali': 'http://localhost:8001',
            'websearch': 'http://localhost:8002',
            'owasp': 'http://localhost:8003',
            'rag': 'http://localhost:8004',
            'zap': 'http://localhost:8005',
        }

    def run(self, input_data):
        # input_data: dict with 'tool' and 'command'
        tool = input_data.get('tool')
        command = input_data.get('command')
        url = self.mcp_servers.get(tool)
        if not url:
            return {'node': 'MCPClientNode', 'output': f'[ERROR] Unknown tool: {tool}'}
        try:
            resp = requests.post(f'{url}/run', json={'command': command}, timeout=120)
            resp.raise_for_status()
            # If streaming, collect all lines
            if resp.headers.get('content-type', '').startswith('text/plain'):
                response = resp.text
            else:
                response = resp.json()
        except Exception as e:
            response = f'[MCP ERROR] {e}'
        return {'node': 'MCPClientNode', 'output': response} 