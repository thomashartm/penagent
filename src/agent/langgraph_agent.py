from src.agent.planner import Planner
from src.agent.memory import ShortTermMemory
from src.agent.logging_utils import log_thought, log_action, log_observation, log_debug
import re

class LangGraphAgent:
    """Autonomous pentesting agent using langgraph."""

    XSS_PAYLOADS = [
        '<script>alert(1)</script>',
        '" onmouseover=alert(1) "',
        "'><img src=x onerror=alert(1)>",
        '<svg/onload=alert(1)>',
        '<body onload=alert(1)>',
        '<iframe src=javascript:alert(1)>',
        '<math href="javascript:alert(1)">CLICK',
    ]

    def __init__(self, tools=None, llm=None):
        """Initialize agent with tools and LLM backend."""
        self.tools = {tool.__class__.__name__: tool for tool in (tools or [])}
        self.llm = llm
        self.memory = ShortTermMemory()
        self.planner = Planner()

    def plan(self, goal):
        """Break down high-level goal into discrete steps."""
        steps = self.planner.plan(goal)
        return steps

    def thought(self, context):
        system_prompt = """
You are an autonomous pentesting agent.
For each step, select and use one of the following tools by outputting a command in the format:
Use <ToolName>: <arguments>
Available tools:
- ShellTool: for running shell commands (e.g., nmap, sqlmap, nslookup, dig, traceroute)
- PythonREPLTool: for running Python code
- WebBrowserTool: for browsing or screenshots
- WebSearchTool: for searching the web
- RAGTool: for retrieving domain-specific docs
- KaliContainerTool: for running advanced Linux and pentest commands inside a Kali Linux Docker container (e.g., metasploit, hydra, nikto, gobuster, etc.)
Always use ShellTool for basic network scanning, port scanning, or DNS lookups. Use KaliContainerTool for advanced Linux/pentest tools.
When testing for XSS, try multiple payloads (e.g., <script>alert(1)</script>, "><img src=x onerror=alert(1)>, etc.). After each test, analyze the output for evidence of XSS (e.g., reflected payload, script execution). If no vulnerability is found, try the next payload. Continue until a vulnerability is found or all payloads are exhausted.
If a command fails with 'command not found', use KaliContainerTool to install it:
Use KaliContainerTool: apt update && apt install -y <tool>
Then retry the original command.
Only output a single line in the format above. Do not explain your reasoning.
Examples:
Task: Test for reflected XSS on https://example.com/search?q=test.
Use WebBrowserTool: browse https://example.com/search?q=<script>alert(1)</script>
Task: Test for reflected XSS on https://example.com/search?q=test with payload '" onmouseover=alert(1) "'.
Use WebBrowserTool: browse https://example.com/search?q=" onmouseover=alert(1) "
Task: Run metasploit to scan example.com.
Use KaliContainerTool: msfconsole -q -x 'db_nmap -A example.com; exit'
Task: Use gobuster to enumerate directories on https://example.com.
Use KaliContainerTool: gobuster dir -u https://example.com -w /usr/share/wordlists/dirb/common.txt
Task: Scan example.com for open ports.
Use ShellTool: nmap -Pn example.com
"""
        prompt = (
            system_prompt +
            f"Context: {context}\nHistory: {self.memory.get_history()}\nWhat should the agent do next?"
        )
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
                for payload in self.XSS_PAYLOADS:
                    test_url = re.sub(r'(q=)[^&]*', f"\\1{payload}", url) if 'q=' in url else url
                    context['current_step'] = f"Testing XSS payload: {payload}"
                    thought = f"Use WebBrowserTool: browse {test_url}"
                    action_result = self.action(thought)
                    obs = self.observation(action_result)
                    # Analyze with LLM if XSS is found
                    analysis_prompt = f"Analyze the following page content for evidence of XSS: {action_result.get('content', '')}\nPayload: {payload}\nDid the payload appear in the response or trigger script execution?"
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