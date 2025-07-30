"""
CLI interface for the security testing orchestration system.
Pure UI layer that uses the app_api for business logic.
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
from rich.live import Live
from rich.layout import Layout
from rich.columns import Columns
from rich.align import Align
import json
import nest_asyncio

# Enable nested event loops
nest_asyncio.apply()

from .app_api import (
    chat as api_chat, security_scan, get_job_status, cancel_job, get_job_history,
    StreamResponse, ResponseType, JobStatus
)

app = typer.Typer(help="Security Testing Orchestration CLI.\n\n"
    "You can use OpenAI (default) or local Ollama models.\n"
    "For Ollama, use --model ollama/llama3 (or any local model name).\n"
)
console = Console()


@app.command()
def scan(
    target: str = typer.Argument(..., help="Target for security testing (domain, IP, or URL)"),
    message: str = typer.Option(None, "--message", "-m", help="Custom message or instructions"),
    model: str = typer.Option("ollama/llama3", "--model", help="LLM model to use (e.g. ollama/llama3)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Conduct security testing on a target."""
    if verbose:
        console.print(f"🎯 Target: {target}")
        console.print(f"💬 Message: {message or 'Default security scan'}")
        console.print(f"🤖 Model: {model}")
    
    # Default message if none provided
    if not message:
        message = f"Conduct a comprehensive security assessment of {target}"
    
    def run_scan():
        asyncio.run(run_security_scan_ui(target, message, model, verbose))
    
    run_scan()


@app.command()
def chat(
    message: str = typer.Argument(..., help="Message to send to the AI assistant"),
    model: str = typer.Option("ollama/llama3", "--model", help="LLM model to use (e.g. ollama/llama3)")
):
    """Chat with the AI assistant."""
    console.print(f"💬 Message: {message}")
    console.print(f"🤖 Model: {model}")
    
    def run_chat():
        asyncio.run(run_chat_ui(message, model))
    
    run_chat()


@app.command()
def status(
    job_id: str = typer.Argument(..., help="Job ID to check status")
):
    """Check status of a specific job."""
    job_info = get_job_status(job_id)
    if job_info:
        display_job_status(job_info)
    else:
        console.print(f"❌ Job {job_id} not found", style="red")


@app.command()
def history(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of jobs to show")
):
    """Show job history."""
    jobs = get_job_history(limit)
    display_job_history(jobs)


@app.command()
def cancel(
    job_id: str = typer.Argument(..., help="Job ID to cancel")
):
    """Cancel a running job."""
    if cancel_job(job_id):
        console.print(f"✅ Job {job_id} cancelled", style="green")
    else:
        console.print(f"❌ Failed to cancel job {job_id}", style="red")


async def run_security_scan_ui(target: str, message: str, model: str, verbose: bool):
    """Run security scan with UI updates."""
    try:
        console.print(Panel.fit(
            f"🚀 Starting Security Assessment\n\n"
            f"Target: {target}\n"
            f"Message: {message}\n"
            f"Model: {model}",
            title="Security Testing Orchestrator",
            border_style="blue"
        ))
        
        # Stream responses from API
        async for response in security_scan(target, message, model):
            await handle_stream_response(response, verbose)
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)


async def run_chat_ui(message: str, model: str):
    """Run chat with UI updates."""
    try:
        console.print(Panel.fit(
            f"💬 Chat Mode\n\n"
            f"Message: {message}\n"
            f"Model: {model}",
            title="AI Assistant",
            border_style="green"
        ))
        
        # Stream responses from API
        async for response in api_chat(message, model):
            await handle_stream_response(response, verbose=False)
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)


async def handle_stream_response(response: StreamResponse, verbose: bool):
    """Handle streaming responses and update UI."""
    if response.type == ResponseType.STATUS:
        console.print(f"🔄 {response.data['message']}", style="yellow")
        
    elif response.type == ResponseType.CHAT:
        console.print(Panel(
            response.data["response"],
            title="AI Response",
            border_style="green"
        ))
        
    elif response.type == ResponseType.SECURITY_SCAN:
        display_security_scan_results(response.data, verbose)
        
    elif response.type == ResponseType.ERROR:
        console.print(f"❌ Error: {response.data['error']}", style="red")
        
    elif response.type == ResponseType.PROGRESS:
        if verbose:
            console.print(f"📊 Progress: {response.data.get('message', '')}", style="cyan")


def display_security_scan_results(data: dict, verbose: bool):
    """Display security scan results."""
    # Display intent and confidence
    if "intent" in data:
        console.print(f"\n🎯 Intent: {data['intent']}")
    
    # Display security plan
    if data.get("security_plan"):
        plan = data["security_plan"]
        console.print(f"\n📋 Security Plan:")
        console.print(f"   Target: {plan['target']}")
        console.print(f"   Phases: {', '.join(plan['phases'])}")
        console.print(f"   Priority: {plan['priority']}")
        console.print(f"   Scope: {plan['scope']}")
    
    # Display phase results
    if data.get("phase_results"):
        console.print(f"\n📊 Phase Results:")
        
        table = Table(title="Security Testing Phases")
        table.add_column("Phase", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Duration", style="yellow")
        table.add_column("Tools Used", style="blue")
        table.add_column("Findings", style="magenta")
        
        for result in data["phase_results"]:
            status = "✅ Success" if result["success"] else "❌ Failed"
            duration = f"{result['duration']:.2f}s"
            tools = ", ".join(result["tools_used"]) if result["tools_used"] else "None"
            findings_count = result["findings_count"]
            
            table.add_row(
                result["phase"].replace("_", " ").title(),
                status,
                duration,
                tools,
                str(findings_count)
            )
        
        console.print(table)
        
        if verbose:
            console.print(f"\n🔍 Detailed Findings:")
            for result in data["phase_results"]:
                if result["findings"]:
                    console.print(f"\n📋 {result['phase'].replace('_', ' ').title()}:")
                    for finding in result["findings"]:
                        console.print(f"   • {finding}")
    
    # Display final report
    if data.get("final_report"):
        console.print(f"\n📄 Final Report:")
        console.print(Panel(
            data["final_report"],
            title="Security Assessment Report",
            border_style="blue"
        ))


def display_job_status(job_info):
    """Display job status information."""
    console.print(Panel(
        f"Job ID: {job_info.job_id}\n"
        f"Status: {job_info.status.value}\n"
        f"Created: {job_info.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Updated: {job_info.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Target: {job_info.target or 'N/A'}\n"
        f"Message: {job_info.message or 'N/A'}\n"
        f"Model: {job_info.model or 'N/A'}\n"
        f"Error: {job_info.error or 'None'}",
        title="Job Status",
        border_style="blue"
    ))


def display_job_history(jobs):
    """Display job history."""
    if not jobs:
        console.print("No jobs found.", style="yellow")
        return
    
    table = Table(title="Job History")
    table.add_column("Job ID", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Target", style="blue")
    table.add_column("Created", style="yellow")
    table.add_column("Duration", style="magenta")
    
    for job in jobs:
        duration = job.updated_at - job.created_at
        duration_str = f"{duration.total_seconds():.1f}s"
        
        table.add_row(
            job.job_id,
            job.status.value,
            job.target or "N/A",
            job.created_at.strftime("%Y-%m-%d %H:%M"),
            duration_str
        )
    
    console.print(table)


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