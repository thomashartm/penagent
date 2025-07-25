from src.agent.planner import Planner
from src.agent.memory import ShortTermMemory
from src.agent.logging_utils import log_thought, log_action, log_observation, log_debug, set_log_paths
from src.prompts.agent_instructions import AGENT_SYSTEM_PROMPT
from src.prompts.xss_loop import XSS_SYSTEM_PROMPT, XSS_PAYLOADS
import re
import os

class LangGraphAgent:
    """Autonomous pentesting agent using langgraph."""

    def __init__(self, tools=None, llm=None, output_dir=None):
        """Initialize agent with tools, LLM backend, and output directory."""
        self.tools = {tool.__class__.__name__: tool for tool in (tools or [])}
        self.llm = llm
        self.memory = ShortTermMemory()
        self.planner = Planner()
        self.output_dir = output_dir or '.'
        os.makedirs(self.output_dir, exist_ok=True)
        set_log_paths(
            os.path.join(self.output_dir, 'process_logs.json'),
            os.path.join(self.output_dir, 'agent_debug.log')
        )

    def plan(self, goal):
        steps = self.planner.plan(goal)
        return steps

    def agent_prompt(self, context):
        return (
            AGENT_SYSTEM_PROMPT +
            f"Context: {context}\nHistory: {self.memory.get_history()}\nWhat should the agent do next?"
        )

    def xss_prompt(self, context):
        return (
            AGENT_SYSTEM_PROMPT +
            XSS_SYSTEM_PROMPT +
            f"Context: {context}\nHistory: {self.memory.get_history()}\nWhat should the agent do next?"
        )

    def thought(self, context, xss_mode=False):
        prompt = self.xss_prompt(context) if xss_mode else self.agent_prompt(context)
        thought = self.llm.generate(prompt)
        log_thought(thought)
        self.memory.add({'type': 'Thought', 'content': thought})
        return thought

    def action(self, thought):
        match = re.search(r'Use (\w+): (.+)', thought)
        if not match:
            action_result = {'error': 'No tool/action specified'}
            log_action(action_result)
            self.memory.add({'type': 'Action', 'content': action_result})
            return action_result
        tool_name, arg = match.groups()
        tool = self.tools.get(tool_name)
        if not tool:
            action_result = {'error': f'Tool {tool_name} not found'}
            log_action(action_result)
            self.memory.add({'type': 'Action', 'content': action_result})
            return action_result
        # Dispatch to tool
        if hasattr(tool, 'execute'):
            action_result = tool.execute(arg)
        elif hasattr(tool, 'browse'):
            action_result = tool.browse(arg)
        elif hasattr(tool, 'search'):
            action_result = tool.search(arg)
        elif hasattr(tool, 'retrieve'):
            action_result = tool.retrieve(arg)
        else:
            action_result = {'error': f'Tool {tool_name} has no valid method'}
        log_action({'tool': tool_name, 'arg': arg, 'result': action_result})
        self.memory.add({'type': 'Action', 'content': {'tool': tool_name, 'arg': arg, 'result': action_result}})

        # Autonomous tool installation if command not found
        if (
            tool_name == 'KaliContainerTool' and
            isinstance(action_result, dict) and
            'stderr' in action_result and
            'command not found' in action_result['stderr']
        ):
            m = re.search(r'(/bin/bash: line \d+: )?(\w+): command not found', action_result['stderr'])
            if m:
                missing_tool = m.group(2)
                log_debug(f"Detected missing tool: {missing_tool}. Attempting to install in Kali container.")
                install_cmd = f"apt update && apt install -y {missing_tool}"
                install_result = tool.execute(install_cmd)
                log_action({'tool': tool_name, 'arg': install_cmd, 'result': install_result})
                self.memory.add({'type': 'Action', 'content': {'tool': tool_name, 'arg': install_cmd, 'result': install_result}})
                retry_result = tool.execute(arg)
                log_action({'tool': tool_name, 'arg': arg, 'result': retry_result, 'note': 'Retried after install'})
                self.memory.add({'type': 'Action', 'content': {'tool': tool_name, 'arg': arg, 'result': retry_result, 'note': 'Retried after install'}})
                return retry_result
        return action_result

    def observation(self, action_result):
        """Observe and log the result of the action."""
        log_observation(action_result)
        self.memory.add({'type': 'Observation', 'content': action_result})
        return action_result

    def run(self, goal):
        steps = self.plan(goal)
        context = {'goal': goal, 'steps': steps}
        # XSS processing loop
        if any('xss' in step.lower() for step in steps):
            url = None
            for step in steps:
                m = re.search(r'(https?://\S+)', step)
                if m:
                    url = m.group(1)
                    break
            if url:
                for payload in XSS_PAYLOADS:
                    test_url = re.sub(r'(q=)[^&]*', f"\\1{payload}", url) if 'q=' in url else url
                    context['current_step'] = f"Testing XSS payload: {payload}"
                    thought = f"Use WebBrowserTool: browse {test_url}"
                    action_result = self.action(thought)
                    obs = self.observation(action_result)
                    # Analyze with LLM if XSS is found
                    analysis_prompt = f"{XSS_SYSTEM_PROMPT}\nAnalyze the following page content for evidence of XSS: {action_result.get('content', '')}\nPayload: {payload}\nDid the payload appear in the response or trigger script execution?"
                    analysis = self.llm.generate(analysis_prompt)
                    log_thought(f"XSS Analysis for payload '{payload}': {analysis}")
                    self.memory.add({'type': 'Thought', 'content': f"XSS Analysis for payload '{payload}': {analysis}"})
                    if 'xss' in analysis.lower() or 'vulnerab' in analysis.lower() or 'alert(1)' in analysis.lower():
                        log_debug(f"XSS detected with payload: {payload}")
                        break
                return self.memory.get_history()
        # Default loop
        for step in steps:
            context['current_step'] = step
            thought = self.thought(context)
            action_result = self.action(thought)
            obs = self.observation(action_result)
        return self.memory.get_history() 