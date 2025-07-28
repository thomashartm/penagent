"""
LangGraph orchestrator for security testing phases.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from langchain_community.llms.ollama import Ollama

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
from core.prompts.chat import get_chat_response_prompt
from core.prompts.plan import get_plan_security_test_prompt
from core.prompts.report import get_generate_report_prompt


class SecurityOrchestrator:
    """Main orchestrator for security testing workflow."""
    
    def __init__(self, llm_model: str = "ollama/llama3"):
        # Only Ollama is supported for now. Future: add OpenAI/Gemini here.
        if llm_model.startswith("ollama/"):
            model_name = llm_model.split("/", 1)[1] if "/" in llm_model else "llama3"
            self.llm = Ollama(model=model_name, base_url="http://localhost:11434", temperature=0.1)
        else:
            raise ValueError("Only Ollama is supported in this build. For OpenAI/Gemini, update dependencies and code.")
        self.mcp_manager = MCPClientManager()
        self.strategies = {
            SecurityPhase.INFORMATION_GATHERING: InformationGatheringStrategy(),
            SecurityPhase.SPIDERING: SpideringStrategy(),
            SecurityPhase.ACTIVE_SCANNING: ActiveScanningStrategy(),
            SecurityPhase.EVALUATION: EvaluationStrategy()
        }
    
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
            SystemMessage(content="You are an AI assistant that analyzes user intent for security testing."),
            HumanMessage(content=prompt)
        ]
        response = await self.llm.ainvoke(messages)
        content = response
        # Parse response (simplified - in production, use structured output)
        intent = UserIntent.CHAT if "CHAT" in content.upper() else UserIntent.SECURITY_TESTING
        confidence = 0.8  # Simplified
        reasoning = content
        target = None
        if intent == UserIntent.SECURITY_TESTING:
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
            SystemMessage(content="You are a helpful AI assistant."),
            HumanMessage(content=prompt)
        ]
        response = await self.llm.ainvoke(messages)
        state.chat_response = response
        return state
    
    async def plan_security_test(self, state: WorkflowState) -> WorkflowState:
        """Plan the security testing phases."""
        target = state.intent_decision.target or "example.com"
        prompt = get_plan_security_test_prompt(target, state.user_input.message)
        messages = [
            SystemMessage(content="You are a security testing planner."),
            HumanMessage(content=prompt)
        ]
        response = await self.llm.ainvoke(messages)
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
        async with self.mcp_manager:
            for phase in state.security_plan.phases:
                print(f"\n🔍 Executing {phase.value} phase for {state.security_plan.target}")
                
                start_time = time.time()
                
                # Get phase strategy
                strategy = self.strategies[phase]
                
                # Get previous findings
                previous_findings = []
                for result in state.phase_results:
                    if result.findings:
                        previous_findings.extend(result.findings)
                
                # Execute phase tools
                tool_results = await self.mcp_manager.execute_phase_tools(
                    phase, state.security_plan.target, {"previous_findings": previous_findings}
                )
                
                # Process tool results
                findings = []
                tools_used = []
                
                for result in tool_results:
                    if result.success:
                        tools_used.append(result.tool_name)
                        # Extract findings from tool output (simplified)
                        if result.output and len(result.output) > 50:
                            findings.append(f"{result.tool_name}: {result.output[:200]}...")
                    else:
                        print(f"❌ Tool {result.tool_name} failed: {result.error}")
                
                duration = time.time() - start_time
                
                # Create phase result
                phase_result = PhaseResult(
                    phase=phase,
                    success=len(findings) > 0,
                    findings=findings,
                    tools_used=tools_used,
                    duration=duration
                )
                
                state.phase_results.append(phase_result)
                state.current_phase = phase
                
                print(f"✅ {phase.value} phase completed in {duration:.2f}s")
                print(f"   Tools used: {', '.join(tools_used)}")
                print(f"   Findings: {len(findings)}")
        
        return state
    
    async def generate_report(self, state: WorkflowState) -> WorkflowState:
        """Generate final security assessment report."""
        # Collect all findings
        all_findings = []
        for result in state.phase_results:
            all_findings.extend(result.findings)
        prompt = get_generate_report_prompt(state.security_plan.target, all_findings)
        messages = [
            SystemMessage(content="You are a security assessment report writer."),
            HumanMessage(content=prompt)
        ]
        response = await self.llm.ainvoke(messages)
        state.final_report = response
        return state
    
    def route_by_intent(self, state: WorkflowState) -> str:
        """Route workflow based on detected intent."""
        return state.intent_decision.intent.value
    
    async def run_workflow(self, user_input: str, target: str = None) -> WorkflowState:
        """Run the complete security testing workflow."""
        # Initialize state
        state = WorkflowState(
            user_input=UserInput(
                message=user_input,
                target=target
            )
        )
        
        # Create and run workflow
        workflow = self.create_workflow()
        app = workflow.compile()
        
        # Run the workflow
        final_state = await app.ainvoke(state)
        
        return final_state 