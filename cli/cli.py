#!/usr/bin/env python3
import os
import sys
import click
import json
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.orchestrator import Orchestrator
from core.logger import Logger

@click.group()
def cli():
    """Command line interface for the opsiary system."""
    pass

@cli.command()
@click.argument("agent_name", required=False)
@click.option("--config", default=None, help="Path to the config file")
def run(agent_name, config):
    """Run an agent with the given configuration."""
    # If no agent name is provided, use the current directory
    if not agent_name:
        current_dir = os.getcwd()
        if os.path.basename(os.path.dirname(current_dir)) == "agents":
            agent_name = os.path.basename(current_dir)
        else:
            click.echo("Error: Not in an agent directory and no agent name provided")
            sys.exit(1)
    
    # If no config is provided, try to use config.json in the current directory
    if not config:
        if os.path.exists("config.json"):
            config = "config.json"
        else:
            config = f"agents/{agent_name}/config.json"
            if not os.path.exists(config):
                click.echo(f"Error: No configuration file found for agent {agent_name}")
                sys.exit(1)
    
    # Create a job ID
    job_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Initialize orchestrator and run the agent
    orchestrator = Orchestrator()
    result = orchestrator.run_agent(agent_name, config, job_id)
    
    click.echo(f"Job ID: {job_id}")
    click.echo(f"Status: {result.get('status', 'unknown')}")
    click.echo(f"See logs with: cli.py logs --job-id {job_id}")
    click.echo(f"See results with: cli.py results --job-id {job_id}")

@cli.command("validate-agent")
@click.argument("agent_name")
@click.option("--config", default=None, help="Path to the config file")
def validate_agent(agent_name, config):
    """Validate an agent without running it."""
    if not config:
        config = f"agents/{agent_name}/config.json"
    
    orchestrator = Orchestrator()
    is_valid, message = orchestrator.validate_agent(agent_name, config)
    
    if is_valid:
        click.echo(f"Agent {agent_name} is valid.")
    else:
        click.echo(f"Agent {agent_name} is invalid: {message}")
        sys.exit(1)

@cli.command()
@click.option("--job-id", required=True, help="ID of the job")
def logs(job_id):
    """View logs for a specific job."""
    log_path = f"storage/logs/{job_id}.json"
    
    if not os.path.exists(log_path):
        click.echo(f"Error: No logs found for job {job_id}")
        sys.exit(1)
    
    with open(log_path, "r") as f:
        logs = json.load(f)
    
    click.echo(json.dumps(logs, indent=2))

@cli.command()
@click.option("--job-id", required=True, help="ID of the job")
def results(job_id):
    """View results for a specific job."""
    results_path = f"storage/job_results/{job_id}_results.json"
    
    if not os.path.exists(results_path):
        click.echo(f"Error: No results found for job {job_id}")
        sys.exit(1)
    
    with open(results_path, "r") as f:
        results = json.load(f)
    
    click.echo(json.dumps(results, indent=2))

@cli.command()
@click.argument("resource_type", type=click.Choice(["agents"]))
def list(resource_type):
    """List available resources of the given type."""
    if resource_type == "agents":
        agents_dir = Path("agents")
        agents = [d.name for d in agents_dir.iterdir() if d.is_dir()]
        
        click.echo("Available agents:")
        for agent in agents:
            click.echo(f"  - {agent}")

@cli.command()
@click.option("--job-id", required=True, help="ID of the job")
def status(job_id):
    """Check the status of a job."""
    log_path = f"storage/logs/{job_id}.json"
    
    if not os.path.exists(log_path):
        click.echo(f"Error: No logs found for job {job_id}")
        sys.exit(1)
    
    with open(log_path, "r") as f:
        logs = json.load(f)
    
    click.echo(f"Job ID: {job_id}")
    click.echo(f"Agent: {logs.get('agent', 'unknown')}")
    click.echo(f"Status: {logs.get('status', 'unknown')}")
    click.echo(f"Timestamp: {logs.get('timestamp', 'unknown')}")
    if "metrics" in logs:
        click.echo("Metrics:")
        for key, value in logs["metrics"].items():
            click.echo(f"  {key}: {value}")

if __name__ == "__main__":
    cli()