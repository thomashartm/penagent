"""
CLI entrypoint for the security testing orchestration system.
"""

import asyncio
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import logging
import sys
import os
from datetime import datetime

from .orchestrator import SecurityOrchestrator

app = typer.Typer(help="Security Testing Orchestration CLI.\n\n"
    "You can use OpenAI (default) or local Ollama models.\n"
    "For Ollama, use --model ollama/llama3 (or any local model name).\n"
)
console = Console()

# Generate a job ID for each run (timestamp-based, human readable)
def generate_job_id():
    return datetime.now().strftime("job_%Y%m%d_%H%M%S")

def get_log_dir(job_id):
    log_dir = os.path.join(os.path.dirname(__file__), "..", "outputs", job_id)
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

def get_log_file(job_id):
    return os.path.join(get_log_dir(job_id), "orchestrator_debug.log")

def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        filemode="a",
        format="%(asctime)s %(levelname)s: %(message)s",
        level=logging.INFO
    )


@app.command()
def scan(
    target: str = typer.Argument(..., help="Target for security testing (domain, IP, or URL)"),
    message: str = typer.Option(None, "--message", "-m", help="Custom message or instructions"),
    model: str = typer.Option("ollama/llama3", "--model", help="LLM model to use (e.g. ollama/llama3)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Conduct security testing on a target."""
    job_id = generate_job_id()
    log_file = get_log_file(job_id)
    setup_logging(log_file)
    console.print(f"[bold blue]Job ID:[/bold blue] {job_id}")
    if verbose:
        console.print(f"🎯 Target: {target}")
        console.print(f"💬 Message: {message or 'Default security scan'}")
        console.print(f"🤖 Model: {model}")
    
    # Default message if none provided
    if not message:
        message = f"Conduct a comprehensive security assessment of {target}"
    
    asyncio.run(run_security_scan(target, message, model, verbose, job_id))


@app.command()
def chat(
    message: str = typer.Argument(..., help="Message to send to the AI assistant"),
    model: str = typer.Option("ollama/llama3", "--model", help="LLM model to use (e.g. ollama/llama3)")
):
    """Chat with the AI assistant."""
    job_id = generate_job_id()
    log_file = get_log_file(job_id)
    setup_logging(log_file)
    console.print(f"[bold blue]Job ID:[/bold blue] {job_id}")
    console.print(f"💬 Message: {message}")
    console.print(f"🤖 Model: {model}")
    
    asyncio.run(run_chat(message, model, job_id))


async def run_security_scan(target: str, message: str, model: str, verbose: bool, job_id: str):
    """Run a security scan workflow."""
    try:
        console.print(Panel.fit(
            f"🚀 Starting Security Assessment\n\n"
            f"Target: {target}\n"
            f"Message: {message}\n"
            f"Model: {model}",
            title="Security Testing Orchestrator",
            border_style="blue"
        ))
        # Initialize orchestrator
        orchestrator = SecurityOrchestrator(llm_model=model)
        log_file = get_log_file(job_id)
        # Show spinner while processing
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            task = progress.add_task("Processing...", start=True)
            orig_stdout = sys.stdout
            sys.stdout = open(log_file, "a")
            try:
                final_state = await orchestrator.run_workflow(message, target, job_id=job_id)
            finally:
                sys.stdout.close()
                sys.stdout = orig_stdout
            progress.update(task, description="Done.")
        # Display results
        display_results(final_state, verbose)
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)


async def run_chat(message: str, model: str, job_id: str):
    """Run a chat workflow."""
    try:
        console.print(Panel.fit(
            f"💬 Chat Mode\n\n"
            f"Message: {message}\n"
            f"Model: {model}",
            title="AI Assistant",
            border_style="green"
        ))
        # Initialize orchestrator
        orchestrator = SecurityOrchestrator(llm_model=model)
        log_file = get_log_file(job_id)
        # Show spinner while processing
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            task = progress.add_task("Processing...", start=True)
            orig_stdout = sys.stdout
            sys.stdout = open(log_file, "a")
            try:
                final_state = await orchestrator.run_workflow(message, job_id=job_id)
            finally:
                sys.stdout.close()
                sys.stdout = orig_stdout
            progress.update(task, description="Done.")
        # Ensure final_state is a WorkflowState (handle AddableValuesDict from LangGraph)
        from core.models import WorkflowState
        if not isinstance(final_state, WorkflowState):
            final_state = WorkflowState(**dict(final_state))
        # Display chat response
        if final_state.chat_response:
            console.print(Panel(
                final_state.chat_response,
                title="AI Response",
                border_style="green"
            ))
        else:
            console.print("❌ No response generated", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)


def display_results(state, verbose: bool):
    """Display security assessment results."""
    if state.intent_decision:
        intent = state.intent_decision.intent
        console.print(f"\n🎯 Intent: {intent.value}")
        console.print(f"📊 Confidence: {state.intent_decision.confidence}")
        console.print(f"💭 Reasoning: {state.intent_decision.reasoning}")
    
    if state.security_plan:
        console.print(f"\n📋 Security Plan:")
        console.print(f"   Target: {state.security_plan.target}")
        console.print(f"   Phases: {', '.join([p.value for p in state.security_plan.phases])}")
        console.print(f"   Priority: {state.security_plan.priority}")
        console.print(f"   Scope: {state.security_plan.scope}")
    
    if state.phase_results:
        console.print(f"\n📊 Phase Results:")
        
        table = Table(title="Security Testing Phases")
        table.add_column("Phase", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Duration", style="yellow")
        table.add_column("Tools Used", style="blue")
        table.add_column("Findings", style="magenta")
        
        for result in state.phase_results:
            status = "✅ Success" if result.success else "❌ Failed"
            duration = f"{result.duration:.2f}s"
            tools = ", ".join(result.tools_used) if result.tools_used else "None"
            findings_count = len(result.findings)
            
            table.add_row(
                result.phase.value.replace("_", " ").title(),
                status,
                duration,
                tools,
                str(findings_count)
            )
        
        console.print(table)
        
        if verbose:
            console.print(f"\n🔍 Detailed Findings:")
            for result in state.phase_results:
                if result.findings:
                    console.print(f"\n📋 {result.phase.value.replace('_', ' ').title()}:")
                    for finding in result.findings:
                        console.print(f"   • {finding}")
    
    if state.final_report:
        console.print(f"\n📄 Final Report:")
        console.print(Panel(
            state.final_report,
            title="Security Assessment Report",
            border_style="blue"
        ))


@app.callback()
def main():
    """
    Security Testing Orchestration CLI
    
    This tool provides intelligent security testing orchestration using LangGraph and MCP servers.
    It can either engage in conversation or conduct comprehensive security assessments.
    
    LLM Model Selection:
      - Default: OpenAI (gpt-4, gpt-3.5-turbo, etc.)
      - Local Ollama: Use --model ollama/llama3 (or any local model)
    """
    pass


if __name__ == "__main__":
    app() 