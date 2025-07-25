import subprocess

class ShellTool:
    """Tool for executing shell commands (e.g., nmap, sqlmap)."""
    def execute(self, command):
        """Execute a shell command and return output."""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            return {'error': str(e)} 