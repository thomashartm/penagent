import os
import json
import uuid

class LoggerNode:
    def __init__(self, output_dir, job_id):
        self.output_dir = output_dir
        self.job_id = job_id

    def run(self, state):
        step_id = str(uuid.uuid4())
        filename = os.path.join(self.output_dir, f'logger_{step_id}.json')
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        return {'node': 'LoggerNode', 'output': f'Logged state to {filename}'} 