import subprocess

class KaliContainerTool:
    """
    Tool for executing commands inside a running Kali Linux Docker container.
    By default, uses a container named 'mcp-kali'.
    """
    def __init__(self, container_name='mcp-kali'):
        self.container_name = container_name

    def execute(self, command):
        """Execute a shell command inside the Kali container and return output."""
        try:
            docker_cmd = [
                'docker', 'exec', self.container_name, '/bin/bash', '-l', '-c', command
            ]
            result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=120)
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            return {'error': str(e)} 