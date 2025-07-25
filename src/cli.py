"""
Usage:
    poetry run pentest-agent run --task "Scan https://public-firing-range.appspot.com/ for Reflected XSS"
"""
import click
from rich.console import Console
from rich.panel import Panel
from src.agent.langgraph_agent import LangGraphAgent
from src.agent.ollama_llm import OllamaLLM
from src.tools.shell_tool import ShellTool
from src.tools.python_repl_tool import PythonREPLTool
from src.tools.web_browser_tool import WebBrowserTool
from src.tools.web_search_tool import WebSearchTool
from src.tools.rag_tool import RAGTool
from src.tools.kali_container_tool import KaliContainerTool
from src.agent.reporting import generate_report
import os
import uuid

console = Console()

def stream_history(history):
    for event in history:
        t = event.get('type')
        c = event.get('content')
        if t == 'Thought':
            console.print(Panel(f"[bold yellow]Thought:[/bold yellow]\n{c}", style="yellow"))
        elif t == 'Action':
            console.print(Panel(f"[bold cyan]Action:[/bold cyan]\n{c}", style="cyan"))
        elif t == 'Observation':
            console.print(Panel(f"[bold green]Observation:[/bold green]\n{c}", style="green"))
        else:
            console.print(f"[grey]Unknown event: {event}")

@click.group()
def main():
    """Pentest-Agent: Autonomous Pentesting AI Agent"""
    pass

@main.command()
@click.option('--task', required=True, help='High-level pentest goal/task')
def run(task):
    # Create outputs directory and unique session directory
    os.makedirs('outputs', exist_ok=True)
    session_id = str(uuid.uuid4())
    session_dir = os.path.join('outputs', session_id)
    os.makedirs(session_dir, exist_ok=True)
    console.print(f"[bold magenta]Session UUID:[/bold magenta] {session_id}")
    console.print(f"[bold green]Running pentest task:[/bold green] {task}")
    # Instantiate tools and LLM
    tools = [
        ShellTool(),
        PythonREPLTool(),
        WebBrowserTool(),
        WebSearchTool(),
        RAGTool(),
        KaliContainerTool()
    ]
    llm = OllamaLLM()
    agent = LangGraphAgent(tools=tools, llm=llm, output_dir=session_dir)
    history = agent.run(task)
    stream_history(history)
    console.print(f"[bold green]Pentest task complete. See {session_dir} for all outputs and logs.[/bold green]")

@main.group()
def tools():
    """List or manage tools."""
    pass

@tools.command('list')
def list_tools():
    console.print("[bold blue]Available Tools:[/bold blue]")
    tools = [
        "Shell Tool",
        "Python REPL",
        "Web Browser Tool",
        "Web Search Tool",
        "RAG Tool (Vector Retrieval)",
        "Kali Container Tool (Docker)"
    ]
    for t in tools:
        console.print(f"- {t}")

@main.command()
@click.option('--input', required=True, help='Input process_logs.json')
@click.option('--output', required=True, help='Output Markdown report')
def report(input, output):
    console.print(f"[bold magenta]Generating report from:[/bold magenta] {input}")
    generate_report(input, output)
    console.print(f"[bold green]Report written to {output}[/bold green]")

if __name__ == "__main__":
    main()

# Advanced extension ideas:
# - Improve prompt templates for more reliable tool selection.
# - Add a tool registry for dynamic tool injection.
# - Implement multi-step planning and subgoal decomposition in Planner.
# - Add streaming LLM output for real-time feedback. 