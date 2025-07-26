from src.agent.planner import Planner
from src.agent.memory import ShortTermMemory
from src.agent.logging_utils import log_thought, log_action, log_observation, log_debug, set_log_paths
from src.prompts.agent_instructions import AGENT_SYSTEM_PROMPT
from src.prompts.owasp_top10 import OWASP_TOP10_PROMPTS
import re
import os
import copy
import time

PIRATE_CHAT_PROMPT = """
You are a friendly AI security assistant with a pirate personality. If the user is not asking for a pentest, investigation, or tool action, respond ONLY in a helpful, friendly, and pirate-themed way. Use pirate lingo, humor, and encouragement. Never suggest or mention any tool, command, or security scan unless the user clearly requests a security test or investigation. If the user asks for security analysis or investigation, switch to your professional mode and proceed with the tools.
"""

class LangGraphAgent:
    """Autonomous pentesting agent using langgraph."""

    def __init__(self, tools=None, llm=None, output_dir=None):
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

    def build_prompt(self, context, state, attack_type=None):
        sys_prompt = AGENT_SYSTEM_PROMPT
        if attack_type and attack_type in OWASP_TOP10_PROMPTS:
            attack_prompt, _ = OWASP_TOP10_PROMPTS[attack_type]
            if attack_prompt:
                sys_prompt += '\n' + attack_prompt
        prompt = (
            sys_prompt +
            f"\nCurrent state: {state}\nContext: {context}\nHistory: {self.memory.get_history()}\nWhat should the agent do next?"
        )
        return prompt

    def pirate_chat(self, user_input):
        prompt = PIRATE_CHAT_PROMPT + f"\nUser: {user_input}\nPirate AI:"
        response = self.llm.generate(prompt)
        log_thought(f"[PIRATE CHAT] {response}")
        self.memory.add({'type': 'Thought', 'content': f'[PIRATE CHAT] {response}'})
        return response

    def should_investigate(self, user_input):
        decision_prompt = (
            "You are a friendly pirate AI security assistant. "
            "If the user is asking for a pentest, scan, investigation, or tool action (like nmap, sqlmap, etc.), reply with exactly INVESTIGATE. "
            "If the user is just chatting, greeting, or asking general questions, reply with exactly PIRATE. "
            "Never suggest a tool unless the user clearly requests a security test or investigation.\n"
            f"User: {user_input}\n"
        )
        decision = self.llm.generate(decision_prompt).strip().upper()
        log_debug(f"[DECISION] {decision}")
        return decision == 'INVESTIGATE'

    def thought(self, context, state, attack_type=None):
        prompt = self.build_prompt(context, state, attack_type)
        thought = self.llm.generate(prompt)
        log_thought(thought)
        self.memory.add({'type': 'Thought', 'content': thought})
        return thought

    def action(self, thought):
        match = re.search(r'Use (\w+): (.+)', thought)
        if not match:
            action_result = {'error': 'No tool/action specified', 'thought': thought}
            log_action(action_result)
            self.memory.add({'type': 'Action', 'content': action_result})
            return action_result
        tool_name, arg = match.groups()
        tool = self.tools.get(tool_name)
        if not tool:
            action_result = {'error': f'Tool {tool_name} not found', 'thought': thought}
            log_action(action_result)
            self.memory.add({'type': 'Action', 'content': action_result})
            return action_result
        if hasattr(tool, 'execute'):
            action_result = tool.execute(arg)
        elif hasattr(tool, 'browse'):
            action_result = tool.browse(arg)
        elif hasattr(tool, 'search'):
            action_result = tool.search(arg)
        elif hasattr(tool, 'retrieve'):
            action_result = tool.retrieve(arg)
        elif hasattr(tool, 'spider'):
            action_result = tool.spider(arg)
        else:
            action_result = {'error': f'Tool {tool_name} has no valid method', 'thought': thought}
        log_action({'tool': tool_name, 'arg': arg, 'result': action_result, 'thought': thought})
        self.memory.add({'type': 'Action', 'content': {'tool': tool_name, 'arg': arg, 'result': action_result, 'thought': thought}})
        return action_result

    def observation(self, action_result):
        """Observe and log the result of the action."""
        log_observation(action_result)
        self.memory.add({'type': 'Observation', 'content': action_result})
        return action_result

    def run(self, user_input, max_steps=100, max_seconds=600):
        # Decision: pirate chat or investigation?
        if not self.should_investigate(user_input):
            pirate_response = self.pirate_chat(user_input)
            # Yield a single event for the frontend chat
            yield {'type': 'PirateChat', 'content': pirate_response}
            return
        # Otherwise, proceed as before
        steps = self.plan(user_input)
        context = {'goal': user_input, 'steps': steps}
        attack_type = None
        for k in OWASP_TOP10_PROMPTS:
            if any(k in step.lower() or k in user_input.lower() for step in steps):
                attack_type = k
                break
        state = {
            'steps': steps,
            'goal': user_input,
            'site_map': [],
            'payloads_left': [],
            'tested': [],
            'vulnerabilities': [],
            'last_action': None,
            'last_observation': None,
            'history': []
        }
        if attack_type and OWASP_TOP10_PROMPTS[attack_type][1]:
            state['payloads_left'] = copy.deepcopy(OWASP_TOP10_PROMPTS[attack_type][1])
        start_time = time.time()
        recent_actions = []  # Track (command, result) tuples
        try:
            for i in range(max_steps):
                if time.time() - start_time > max_seconds:
                    log_thought("[STOP DECISION] Stopping due to max session duration.")
                    self.memory.add({'type': 'Thought', 'content': '[STOP DECISION] Stopping due to max session duration.'})
                    break
                thought = self.thought(context, state, attack_type)
                yield {'type': 'Thought', 'content': thought}
                action_result = self.action(thought)
                yield {'type': 'Action', 'content': action_result}
                obs = self.observation(action_result)
                yield {'type': 'Observation', 'content': obs}
                state['last_action'] = thought
                state['last_observation'] = obs
                state['history'].append({'thought': thought, 'action': action_result, 'observation': obs})
                # --- Automatic stopping if repeated command/result ---
                cmd = None
                result = None
                if isinstance(action_result, dict):
                    cmd = action_result.get('arg')
                    # Use only a summary of result for comparison
                    result = str(action_result.get('result', ''))[:200]
                if cmd and result:
                    recent_actions.append((cmd, result))
                    # Only keep last 4
                    if len(recent_actions) > 4:
                        recent_actions = recent_actions[-4:]
                    # If the same (cmd, result) appears more than once, stop
                    if recent_actions.count((cmd, result)) > 1:
                        log_thought(f"[STOP DECISION] Stopping due to repeated command/result: {cmd}")
                        self.memory.add({'type': 'Thought', 'content': f'[STOP DECISION] Stopping due to repeated command/result: {cmd}'})
                        break
                stop_prompt = (
                    AGENT_SYSTEM_PROMPT +
                    "\nIf you have tried all reasonable actions, are repeating, or are unsure, reply with STOP and a brief reason. "
                    "If you should continue, reply with CONTINUE and a brief reason. "
                    "Be decisive. If you are stuck, reply with STOP. "
                    f"\nCurrent state: {state}\nShould the agent continue testing, try a new payload, change tools, or stop and report? Reply with CONTINUE or STOP and a brief reason."
                )
                stop_decision = self.llm.generate(stop_prompt)
                log_thought(f"[STOP DECISION] {stop_decision}")
                self.memory.add({'type': 'Thought', 'content': f'[STOP DECISION] {stop_decision}'})
                if 'stop' in stop_decision.lower():
                    break
            else:
                log_thought("[STOP DECISION] Stopping due to max step limit.")
                self.memory.add({'type': 'Thought', 'content': '[STOP DECISION] Stopping due to max step limit.'})
        except KeyboardInterrupt:
            log_thought("[STOP DECISION] Stopping due to user interrupt (Ctrl+C).")
            self.memory.add({'type': 'Thought', 'content': '[STOP DECISION] Stopping due to user interrupt (Ctrl+C).'})
        # --- After stopping, have the LLM analyze the results and provide a summary report ---
        report_prompt = (
            AGENT_SYSTEM_PROMPT +
            "\nYou have completed the pentest task. Analyze the actions and observations above and provide a concise summary report of findings, vulnerabilities, and recommendations. Format as Markdown."
            f"\nHistory: {self.memory.get_history()}\nReport:"
        )
        report = self.llm.generate(report_prompt)
        log_thought(f"[REPORT] {report}")
        self.memory.add({'type': 'Report', 'content': report})
        yield {'type': 'Report', 'content': report}
        return self.memory.get_history() 