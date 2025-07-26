# LangGraph workflow scaffold
from src.agent.nodes.planner_node import PlannerNode
from src.agent.nodes.llm_node import LLMNode
from src.agent.nodes.mcp_client_node import MCPClientNode
from src.agent.nodes.logger_node import LoggerNode

class ExpandedWorkflow:
    def __init__(self, output_dir, job_id):
        self.output_dir = output_dir
        self.job_id = job_id
        self.planner = PlannerNode(output_dir, job_id)
        self.llm = LLMNode(output_dir, job_id)
        self.mcp = MCPClientNode(output_dir, job_id)
        self.logger = LoggerNode(output_dir, job_id)

    def run(self, task_prompt):
        plan = self.planner.run(task_prompt)
        yield plan
        # Parse steps from plan output (assume numbered list)
        steps = []
        for line in plan['output'].split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove number or dash
                step = line.split(' ', 1)[-1] if ' ' in line else line
                steps.append(step)
        if not steps:
            steps = [plan['output']]
        for i, step in enumerate(steps):
            llm_out = self.llm.run(f"How should I accomplish this step? {step}")
            yield llm_out
            # For demo, guess tool from step text
            tool = 'kali' if 'nmap' in step or 'scan' in step else 'websearch'
            mcp_input = {'tool': tool, 'command': step}
            mcp_out = self.mcp.run(mcp_input)
            yield mcp_out
            log_out = self.logger.run({'step': step, 'llm': llm_out, 'mcp': mcp_out})
            yield log_out
        yield {'node': 'DONE', 'output': f'Workflow complete for job {self.job_id}'}

def build_workflow(output_dir, job_id):
    return ExpandedWorkflow(output_dir, job_id) 