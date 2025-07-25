import subprocess
import sys

def test_tools_list():
    result = subprocess.run([
        sys.executable, '-m', 'src.cli', 'tools', 'list'
    ], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Shell Tool" in result.stdout
    assert "Python REPL" in result.stdout
    assert "Web Browser Tool" in result.stdout
    assert "Web Search Tool" in result.stdout
    assert "RAG Tool" in result.stdout 