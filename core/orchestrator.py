"""
LangGraph orchestrator for security testing phases.
"""

import asyncio
import time
import socket
import re
from typing import Dict, List, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from langchain_ollama import OllamaLLM
import logging

from .models import (
    WorkflowState, UserInput, IntentDecision, SecurityTestPlan,
    SecurityPhase, PhaseResult, UserIntent
)
from .mcp_client import MCPClientManager
from .strategies.information_gathering import InformationGatheringStrategy
from .strategies.spidering import SpideringStrategy
from .strategies.active_scanning import ActiveScanningStrategy
from .strategies.evaluation import EvaluationStrategy
from core.prompts.intent import get_intent_detection_prompt
from core.prompts.chat import get_chat_response_prompt, get_security_system_prompt
from core.prompts.plan import get_plan_security_test_prompt
from core.prompts.report import get_generate_report_prompt


class SecurityOrchestrator:
    """Main orchestrator for security testing workflow."""
    
    def __init__(self, llm_model: str = "ollama/llama3"):
        # Only Ollama is supported for now. Future: add OpenAI/Gemini here.
        if llm_model.startswith("ollama/"):
            model_name = llm_model.split("/", 1)[1] if "/" in llm_model else "llama3"
            self.llm = OllamaLLM(model=model_name, base_url="http://localhost:11434", temperature=0.1)
        else:
            raise ValueError("Only Ollama is supported in this build. For OpenAI/Gemini, update dependencies and code.")
        self.mcp_manager = MCPClientManager()
        self.strategies = {
            SecurityPhase.INFORMATION_GATHERING: InformationGatheringStrategy(),
            SecurityPhase.SPIDERING: SpideringStrategy(),
            SecurityPhase.ACTIVE_SCANNING: ActiveScanningStrategy(),
            SecurityPhase.EVALUATION: EvaluationStrategy()
        }
    
    def resolve_target_to_ip(self, target: str) -> Dict[str, str]:
        """Resolve target to IP address and return both domain and IP."""
        result = {
            "original_target": target,
            "domain": None,
            "ip_address": None,
            "resolved": False
        }
        
        # Clean the target (remove protocol if present)
        clean_target = re.sub(r'^https?://', '', target.strip())
        
        # Check if it's already an IP address
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if re.match(ip_pattern, clean_target):
            result["ip_address"] = clean_target
            result["resolved"] = True
            return result
        
        # Try to resolve domain to IP
        try:
            # Remove port if present
            domain = clean_target.split(':')[0]
            ip_address = socket.gethostbyname(domain)
            result["domain"] = domain
            result["ip_address"] = ip_address
            result["resolved"] = True
            logging.info(f"Resolved {domain} to {ip_address}")
        except socket.gaierror as e:
            logging.warning(f"Could not resolve {clean_target}: {e}")
            result["domain"] = clean_target
        except Exception as e:
            logging.error(f"Error resolving {clean_target}: {e}")
            result["domain"] = clean_target
        
        return result
    
    def create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("detect_intent", self.detect_intent)
        workflow.add_node("chat_node", self.chat_response)
        workflow.add_node("plan_security_test", self.plan_security_test)
        workflow.add_node("execute_phase", self.execute_phase)
        workflow.add_node("generate_report", self.generate_report)
        
        # Add edges
        workflow.add_edge(START, "detect_intent")
        workflow.add_conditional_edges(
            "detect_intent",
            self.route_by_intent,
            {
                UserIntent.CHAT: "chat_node",
                UserIntent.SECURITY_TESTING: "plan_security_test"
            }
        )
        workflow.add_edge("chat_node", END)
        workflow.add_edge("plan_security_test", "execute_phase")
        workflow.add_edge("execute_phase", "generate_report")
        workflow.add_edge("generate_report", END)
        
        return workflow
    
    async def detect_intent(self, state: WorkflowState) -> WorkflowState:
        """Detect user intent from input."""
        prompt = get_intent_detection_prompt(state.user_input.message)
        messages = [
            SystemMessage(content=get_security_system_prompt()),
            HumanMessage(content=prompt)
        ]
        job_id = state.job_id
        logging.info(f"[{job_id}] LLM intent detection call started.")
        response = await self.llm.ainvoke(messages)
        logging.info(f"[{job_id}] LLM intent detection call finished.")
        content = response
        # Parse response (robust extraction)
        intent = UserIntent.CHAT if "CHAT" in content.upper() else UserIntent.SECURITY_TESTING
        confidence = 0.8  # Simplified
        reasoning = content
        target = None
        if intent == UserIntent.SECURITY_TESTING:
            # Try to extract 'Target:' line from LLM output
            match = re.search(r"Target:\s*(.+)", content)
            if match:
                extracted = match.group(1).strip()
                # Validate as URL/domain/IP
                url_match = re.search(r"(https?://[\w\.-]+|[\w\.-]+\.[a-zA-Z]{2,}|\b\d{1,3}(?:\.\d{1,3}){3}\b)", extracted)
                if url_match:
                    target = url_match.group(1)
                elif extracted.lower() != 'none':
                    target = extracted
            if not target:
                # Fallback: try to extract from user input
                user_input = state.user_input.message
                url_match = re.search(r"(https?://[\w\.-]+|[\w\.-]+\.[a-zA-Z]{2,}|\b\d{1,3}(?:\.\d{1,3}){3}\b)", user_input)
                if url_match:
                    target = url_match.group(1)
            if not target:
                target = state.user_input.target or "example.com"
        state.intent_decision = IntentDecision(
            intent=intent,
            confidence=confidence,
            reasoning=reasoning,
            target=target
        )
        return state
    
    async def chat_response(self, state: WorkflowState) -> WorkflowState:
        """Generate chat response."""
        prompt = get_chat_response_prompt(state.user_input.message)
        messages = [
            SystemMessage(content=get_security_system_prompt()),
            HumanMessage(content=prompt)
        ]
        job_id = state.job_id
        logging.info(f"[{job_id}] LLM chat response call started.")
        response = await self.llm.ainvoke(messages)
        logging.info(f"[{job_id}] LLM chat response call finished.")
        state.chat_response = response
        return state
    
    async def plan_security_test(self, state: WorkflowState) -> WorkflowState:
        """Plan the security testing phases."""
        target = state.intent_decision.target or "example.com"
        prompt = get_plan_security_test_prompt(target, state.user_input.message)
        messages = [
            SystemMessage(content=get_security_system_prompt()),
            HumanMessage(content=prompt)
        ]
        job_id = state.job_id
        logging.info(f"[{job_id}] LLM plan security test call started.")
        response = await self.llm.ainvoke(messages)
        logging.info(f"[{job_id}] LLM plan security test call finished.")
        # Create security plan (simplified)
        state.security_plan = SecurityTestPlan(
            target=target,
            phases=[SecurityPhase.INFORMATION_GATHERING, SecurityPhase.SPIDERING, 
                   SecurityPhase.ACTIVE_SCANNING, SecurityPhase.EVALUATION],
            priority="medium",
            scope="comprehensive"
        )
        return state
    
    async def execute_phase(self, state: WorkflowState) -> WorkflowState:
        """Execute security testing phases."""
        job_id = state.job_id
        
        # Resolve target to IP for tools that need it
        target_info = self.resolve_target_to_ip(state.security_plan.target)
        if target_info["resolved"]:
            print(f"📍 Target resolved: {target_info['domain']} -> {target_info['ip_address']}")
            logging.info(f"[{job_id}] Target resolved: {target_info['domain']} -> {target_info['ip_address']}")
        else:
            print(f"⚠️  Could not resolve {target_info['original_target']} to IP address")
            logging.warning(f"[{job_id}] Could not resolve {target_info['original_target']} to IP address")
        
        async with self.mcp_manager:
            for phase in state.security_plan.phases:
                logging.info(f"[{job_id}] Starting phase: {phase.value} for {state.security_plan.target}")
                print(f"\n🔍 Executing {phase.value} phase for {state.security_plan.target}")
                start_time = time.time()
                # Get phase strategy
                strategy = self.strategies[phase]
                # Get previous findings
                previous_findings = []
                for result in state.phase_results:
                    if result.findings:
                        previous_findings.extend(result.findings)
                
                # Prepare context with resolved IP information
                context = {
                    "previous_findings": previous_findings,
                    "target_info": target_info,
                    "domain": target_info["domain"],
                    "ip_address": target_info["ip_address"]
                }
                
                # Execute phase tools
                logging.info(f"[{job_id}] Executing tools for phase: {phase.value}")
                tool_results = await self.mcp_manager.execute_phase_tools(
                    phase, state.security_plan.target, context
                )
                logging.info(f"[{job_id}] Finished executing tools for phase: {phase.value}")
                # Process tool results
                findings = []
                tools_used = []
                errors = []
                for result in tool_results:
                    logging.info(f"[{job_id}] Tool {result.tool_name} started.")
                    if result.success:
                        tools_used.append(result.tool_name)
                        if result.output:
                            findings.append(f"{result.tool_name}: {result.output}")
                        logging.info(f"[{job_id}] Tool {result.tool_name} finished successfully.")
                    else:
                        error_msg = f"❌ Tool {result.tool_name} failed: {result.error}"
                        print(error_msg)
                        errors.append(error_msg)
                        logging.error(f"[{job_id}] Tool {result.tool_name} failed: {result.error}")
                duration = time.time() - start_time
                # Print findings and errors
                if findings:
                    print(f"   Findings:")
                    for finding in findings:
                        print(f"     - {finding}")
                if errors:
                    print(f"   Errors:")
                    for err in errors:
                        print(f"     - {err}")
                # Create phase result
                phase_result = PhaseResult(
                    phase=phase,
                    success=len(findings) > 0,
                    findings=findings,
                    tools_used=tools_used,
                    duration=duration,
                    error="\n".join(errors) if errors else None
                )
                state.phase_results.append(phase_result)
                state.current_phase = phase
                logging.info(f"[{job_id}] Phase {phase.value} completed in {duration:.2f}s. Tools used: {', '.join(tools_used) if tools_used else 'None'}")
                print(f"✅ {phase.value} phase completed in {duration:.2f}s")
                print(f"   Tools used: {', '.join(tools_used) if tools_used else 'None'}")
        return state
    
    async def generate_report(self, state: WorkflowState) -> WorkflowState:
        """Generate final security assessment report."""
        job_id = state.job_id
        # Collect all findings and errors
        all_findings = []
        all_errors = []
        for result in state.phase_results:
            if result.findings:
                all_findings.extend(result.findings)
            if result.error:
                all_errors.append(result.error)
        prompt = get_generate_report_prompt(state.security_plan.target, all_findings)
        messages = [
            SystemMessage(content=get_security_system_prompt()),
            HumanMessage(content=prompt)
        ]
        logging.info(f"[{job_id}] LLM report generation call started.")
        response = await self.llm.ainvoke(messages)
        logging.info(f"[{job_id}] LLM report generation call finished.")
        # Append errors to the report if any
        if all_errors:
            response += "\n\nErrors encountered during testing:\n" + "\n".join(all_errors)
        state.final_report = response
        return state
    
    def route_by_intent(self, state: WorkflowState) -> str:
        """Route workflow based on detected intent."""
        return state.intent_decision.intent.value
    
    async def run_workflow(self, user_input: str, target: str = None, job_id: str = None) -> WorkflowState:
        """Run the complete security testing workflow."""
        # Initialize state
        state = WorkflowState(
            user_input=UserInput(
                message=user_input,
                target=target
            ),
            job_id=job_id
        )
        
        # Create and run workflow
        workflow = self.create_workflow()
        app = workflow.compile()
        
        # Run the workflow
        final_state = await app.ainvoke(state)
        
        return final_state 