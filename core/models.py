"""
Pydantic models for the core security testing orchestration system.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class SecurityPhase(str, Enum):
    """Enumeration of security testing phases."""
    INFORMATION_GATHERING = "information_gathering"
    SPIDERING = "spidering"
    ACTIVE_SCANNING = "active_scanning"
    EVALUATION = "evaluation"


class UserIntent(str, Enum):
    """Enumeration of user intent types."""
    CHAT = "chat"
    SECURITY_TESTING = "security_testing"


class UserInput(BaseModel):
    """Model for user input processing."""
    message: str = Field(..., description="The user's input message")
    target: Optional[str] = Field(None, description="Target for security testing")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class IntentDecision(BaseModel):
    """Model for LLM intent decision."""
    intent: UserIntent = Field(..., description="The determined user intent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the decision")
    reasoning: str = Field(..., description="Reasoning for the decision")
    target: Optional[str] = Field(None, description="Extracted target if security testing")


class SecurityTestPlan(BaseModel):
    """Model for security testing plan."""
    target: str = Field(..., description="Target for security testing")
    phases: List[SecurityPhase] = Field(..., description="Planned security testing phases")
    priority: str = Field(default="medium", description="Priority level (low, medium, high, critical)")
    scope: str = Field(default="comprehensive", description="Scope of testing")


class PhaseResult(BaseModel):
    """Model for phase execution results."""
    phase: SecurityPhase = Field(..., description="The security testing phase")
    success: bool = Field(..., description="Whether the phase completed successfully")
    findings: List[str] = Field(default_factory=list, description="Findings from this phase")
    tools_used: List[str] = Field(default_factory=list, description="Tools used in this phase")
    duration: float = Field(..., description="Duration of phase execution in seconds")
    error: Optional[str] = Field(None, description="Error message if phase failed")


class WorkflowState(BaseModel):
    """Model for LangGraph workflow state."""
    user_input: UserInput = Field(..., description="Original user input")
    intent_decision: Optional[IntentDecision] = Field(None, description="LLM intent decision")
    security_plan: Optional[SecurityTestPlan] = Field(None, description="Security testing plan")
    current_phase: Optional[SecurityPhase] = Field(None, description="Current security testing phase")
    phase_results: List[PhaseResult] = Field(default_factory=list, description="Results from completed phases")
    chat_response: Optional[str] = Field(None, description="Response for chat intent")
    final_report: Optional[str] = Field(None, description="Final security testing report")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    job_id: Optional[str] = Field(None, description="Job ID for tracking and logging")


class MCPToolResult(BaseModel):
    """Model for MCP tool execution results."""
    tool_name: str = Field(..., description="Name of the executed tool")
    success: bool = Field(..., description="Whether tool execution was successful")
    output: str = Field(..., description="Tool output")
    error: Optional[str] = Field(None, description="Error message if tool failed")
    duration: float = Field(..., description="Tool execution duration in seconds")


class SecurityFinding(BaseModel):
    """Model for security findings."""
    title: str = Field(..., description="Finding title")
    description: str = Field(..., description="Finding description")
    severity: str = Field(..., description="Severity level (low, medium, high, critical)")
    phase: SecurityPhase = Field(..., description="Phase where finding was discovered")
    evidence: str = Field(..., description="Evidence supporting the finding")
    recommendation: str = Field(..., description="Recommendation for remediation") 