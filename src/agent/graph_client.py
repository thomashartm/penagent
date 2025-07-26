import os
import uuid
from src.agent.langgraph_workflow import build_workflow

class GraphClient:
    def __init__(self):
        self.job_id = str(uuid.uuid4())
        self.output_dir = os.path.join('outputs', self.job_id)
        os.makedirs(self.output_dir, exist_ok=True)
        self.workflow = build_workflow(self.output_dir, self.job_id)

    def run(self, task_prompt):
        # Start the workflow and stream outputs
        for output in self.workflow.run(task_prompt):
            # Log each output to process_logs.json
            with open(os.path.join(self.output_dir, 'process_logs.json'), 'a') as f:
                f.write(str(output) + '\n')
            yield output 