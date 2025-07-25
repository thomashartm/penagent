import io
import contextlib

class PythonREPLTool:
    """Tool for executing Python code snippets for analysis/parsing."""
    def execute(self, code):
        """Execute Python code and return output/result."""
        output = io.StringIO()
        local_vars = {}
        try:
            with contextlib.redirect_stdout(output):
                exec(code, {}, local_vars)
            return {'output': output.getvalue(), 'locals': local_vars}
        except Exception as e:
            return {'error': str(e)} 