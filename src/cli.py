"""
Usage:
    poetry run pentest-agent run --task "Scan https://public-firing-range.appspot.com/ for Reflected XSS"
"""
import click
from src.agent.graph_client import GraphClient

@click.group()
def cli():
    pass

@cli.command()
@click.option('--command', required=True, help='High-level pentest goal or chat prompt')
def run(command):
    """Run a pentest-agent job with the given high-level command."""
    client = GraphClient()
    for output in client.run(command):
        print(output, flush=True)

if __name__ == '__main__':
    cli() 