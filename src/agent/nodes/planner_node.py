from src.agent.nodes.llm_node import LLMNode

class PlannerNode:
    def __init__(self, output_dir, job_id):
        self.output_dir = output_dir
        self.job_id = job_id
        self.llm = LLMNode(output_dir, job_id)

    def run(self, task_prompt):
        planning_prompt = f"Break down the following pentest goal into actionable steps. Output as a numbered list.\nGoal: {task_prompt}"
        plan_result = self.llm.run(planning_prompt)
        return {'node': 'PlannerNode', 'output': plan_result['output']} 