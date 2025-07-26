import requests
import json

class LLMNode:
    def __init__(self, output_dir, job_id, model='llama3'):
        self.output_dir = output_dir
        self.job_id = job_id
        self.model = model
        self.ollama_url = 'http://localhost:11434/api/generate'

    def run(self, input_data):
        prompt = input_data if isinstance(input_data, str) else str(input_data)
        payload = {
            'model': self.model,
            'prompt': prompt,
            'stream': False
        }
        try:
            resp = requests.post(self.ollama_url, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            response = data.get('response', '')
        except Exception as e:
            response = f'[LLM ERROR] {e}'
        return {'node': 'LLMNode', 'output': response} 