import requests
import json

class OllamaLLM:
    """LLM backend using Ollama's local API."""
    def __init__(self, base_url="http://localhost:11434", model="llama3"):
        self.base_url = base_url
        self.model = model

    def generate(self, prompt):
        """Send prompt to Ollama and return response text (handles streaming JSON lines)."""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt},
                timeout=120,
                stream=True
            )
            response.raise_for_status()
            output = ""
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line.decode('utf-8'))
                    output += data.get("response", "")
                except Exception as e:
                    continue  # skip malformed lines
            return output
        except Exception as e:
            return f"[Ollama LLM error: {e}]" 