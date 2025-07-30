"""
UI-agnostic API layer for security testing orchestration.
Handles business logic, job management, and streaming responses.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import AsyncGenerator, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json

from .orchestrator import SecurityOrchestrator
from .models import WorkflowState, UserInput, IntentDecision, SecurityTestPlan, PhaseResult


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResponseType(str, Enum):
    """Response type enumeration."""
    CHAT = "chat"
    SECURITY_SCAN = "security_scan"
    ERROR = "error"
    STATUS = "status"
    PROGRESS = "progress"


@dataclass
class JobInfo:
    """Job information container."""
    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    target: Optional[str] = None
    message: Optional[str] = None
    model: Optional[str] = None
    error: Optional[str] = None
    result: Optional[WorkflowState] = None


@dataclass
class StreamResponse:
    """Streaming response container."""
    type: ResponseType
    job_id: str
    data: Dict[str, Any]
    timestamp: datetime


class SecurityAppAPI:
    """UI-agnostic API for security testing orchestration."""
    
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        self.jobs: Dict[str, JobInfo] = {}
        self.orchestrators: Dict[str, SecurityOrchestrator] = {}
        self._setup_output_dir()
    
    def _setup_output_dir(self):
        """Setup output directory structure."""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "logs"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "reports"), exist_ok=True)
    
    def generate_job_id(self) -> str:
        """Generate a unique job ID."""
        return datetime.now().strftime("job_%Y%m%d_%H%M%S")
    
    def get_log_file(self, job_id: str) -> str:
        """Get log file path for a job."""
        return os.path.join(self.output_dir, "logs", f"{job_id}.log")
    
    def setup_logging(self, job_id: str) -> None:
        """Setup logging for a specific job."""
        log_file = self.get_log_file(job_id)
        logging.basicConfig(
            filename=log_file,
            filemode="a",
            format="%(asctime)s %(levelname)s: %(message)s",
            level=logging.INFO
        )
    
    def create_job(self, target: Optional[str] = None, message: str = "", model: str = "ollama/llama3") -> str:
        """Create a new job and return job ID."""
        job_id = self.generate_job_id()
        job_info = JobInfo(
            job_id=job_id,
            status=JobStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            target=target,
            message=message,
            model=model
        )
        self.jobs[job_id] = job_info
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[JobInfo]:
        """Get job status and information."""
        return self.jobs.get(job_id)
    
    def update_job_status(self, job_id: str, status: JobStatus, error: Optional[str] = None, result: Optional[WorkflowState] = None):
        """Update job status and information."""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.status = status
            job.updated_at = datetime.now()
            if error:
                job.error = error
            if result:
                job.result = result
    
    async def start_chat(self, message: str, model: str = "ollama/llama3") -> AsyncGenerator[StreamResponse, None]:
        """Start a chat conversation and stream responses."""
        job_id = self.create_job(message=message, model=model)
        self.setup_logging(job_id)
        
        try:
            # Update job status
            self.update_job_status(job_id, JobStatus.RUNNING)
            yield StreamResponse(
                type=ResponseType.STATUS,
                job_id=job_id,
                data={"status": "running", "message": "Starting chat conversation..."},
                timestamp=datetime.now()
            )
            
            # Initialize orchestrator
            orchestrator = SecurityOrchestrator(llm_model=model)
            self.orchestrators[job_id] = orchestrator
            
            # Run workflow
            final_state = await orchestrator.run_workflow(message, job_id=job_id)
            
            # Convert AddableValuesDict to WorkflowState if needed
            if not isinstance(final_state, WorkflowState):
                final_state = WorkflowState(**dict(final_state))
            
            # Update job status
            self.update_job_status(job_id, JobStatus.COMPLETED, result=final_state)
            
            # Yield final response
            yield StreamResponse(
                type=ResponseType.CHAT,
                job_id=job_id,
                data={
                    "response": final_state.chat_response,
                    "intent": final_state.intent_decision.intent.value if final_state.intent_decision else "chat",
                    "confidence": final_state.intent_decision.confidence if final_state.intent_decision else 0.0
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Chat failed: {str(e)}"
            self.update_job_status(job_id, JobStatus.FAILED, error=error_msg)
            yield StreamResponse(
                type=ResponseType.ERROR,
                job_id=job_id,
                data={"error": error_msg},
                timestamp=datetime.now()
            )
    
    async def start_security_scan(self, target: str, message: str = "", model: str = "ollama/llama3") -> AsyncGenerator[StreamResponse, None]:
        """Start a security scan and stream progress and results."""
        job_id = self.create_job(target=target, message=message, model=model)
        self.setup_logging(job_id)
        
        try:
            # Update job status
            self.update_job_status(job_id, JobStatus.RUNNING)
            yield StreamResponse(
                type=ResponseType.STATUS,
                job_id=job_id,
                data={"status": "running", "message": "Starting security assessment..."},
                timestamp=datetime.now()
            )
            
            # Initialize orchestrator
            orchestrator = SecurityOrchestrator(llm_model=model)
            self.orchestrators[job_id] = orchestrator
            
            # Default message if none provided
            if not message:
                message = f"Conduct a comprehensive security assessment of {target}"
            
            # Run workflow with progress streaming
            final_state = await self._run_workflow_with_progress(orchestrator, message, target, job_id)
            
            # Convert AddableValuesDict to WorkflowState if needed
            if not isinstance(final_state, WorkflowState):
                final_state = WorkflowState(**dict(final_state))
            
            # Update job status
            self.update_job_status(job_id, JobStatus.COMPLETED, result=final_state)
            
            # Yield final results
            yield StreamResponse(
                type=ResponseType.SECURITY_SCAN,
                job_id=job_id,
                data={
                    "target": target,
                    "intent": final_state.intent_decision.intent.value if final_state.intent_decision else "security_testing",
                    "security_plan": {
                        "target": final_state.security_plan.target,
                        "phases": [p.value for p in final_state.security_plan.phases],
                        "priority": final_state.security_plan.priority,
                        "scope": final_state.security_plan.scope
                    } if final_state.security_plan else None,
                    "phase_results": [
                        {
                            "phase": result.phase.value,
                            "success": result.success,
                            "duration": result.duration,
                            "tools_used": result.tools_used,
                            "findings_count": len(result.findings),
                            "findings": result.findings,
                            "error": result.error
                        } for result in final_state.phase_results
                    ],
                    "final_report": final_state.final_report
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Security scan failed: {str(e)}"
            self.update_job_status(job_id, JobStatus.FAILED, error=error_msg)
            yield StreamResponse(
                type=ResponseType.ERROR,
                job_id=job_id,
                data={"error": error_msg},
                timestamp=datetime.now()
            )
    
    async def _run_workflow_with_progress(self, orchestrator: SecurityOrchestrator, message: str, target: str, job_id: str) -> WorkflowState:
        """Run workflow with progress streaming."""
        # Create initial state
        from .models import UserInput
        state = WorkflowState(
            user_input=UserInput(message=message, target=target),
            job_id=job_id
        )
        
        # Create and run workflow
        workflow = orchestrator.create_workflow()
        app = workflow.compile()
        
        # Run the workflow
        final_state = await app.ainvoke(state)
        return final_state
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            if job.status == JobStatus.RUNNING:
                job.status = JobStatus.CANCELLED
                job.updated_at = datetime.now()
                return True
        return False
    
    def get_job_history(self, limit: int = 50) -> list[JobInfo]:
        """Get job history."""
        sorted_jobs = sorted(self.jobs.values(), key=lambda x: x.created_at, reverse=True)
        return sorted_jobs[:limit]
    
    def cleanup_jobs(self, older_than_days: int = 7) -> int:
        """Clean up old jobs and their files."""
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        cleaned_count = 0
        
        for job_id, job in list(self.jobs.items()):
            if job.created_at < cutoff_date:
                # Remove job from memory
                del self.jobs[job_id]
                
                # Remove orchestrator if exists
                if job_id in self.orchestrators:
                    del self.orchestrators[job_id]
                
                # Remove log file
                log_file = self.get_log_file(job_id)
                if os.path.exists(log_file):
                    os.remove(log_file)
                
                cleaned_count += 1
        
        return cleaned_count


# Global API instance
app_api = SecurityAppAPI()


# Convenience functions for easy access
async def chat(message: str, model: str = "ollama/llama3") -> AsyncGenerator[StreamResponse, None]:
    """Start a chat conversation."""
    async for response in app_api.start_chat(message, model):
        yield response


async def security_scan(target: str, message: str = "", model: str = "ollama/llama3") -> AsyncGenerator[StreamResponse, None]:
    """Start a security scan."""
    async for response in app_api.start_security_scan(target, message, model):
        yield response


def get_job_status(job_id: str) -> Optional[JobInfo]:
    """Get job status."""
    return app_api.get_job_status(job_id)


def cancel_job(job_id: str) -> bool:
    """Cancel a job."""
    return app_api.cancel_job(job_id)


def get_job_history(limit: int = 50) -> list[JobInfo]:
    """Get job history."""
    return app_api.get_job_history(limit) 