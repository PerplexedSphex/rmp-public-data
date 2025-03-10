#!/usr/bin/env python3
import os
import sys
import click
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.prompt_manager import cli as prompt_cli

@click.group()
def cli():
    """Command line utility for prompt management."""
    pass

# Add prompt-cli commands
cli.add_command(prompt_cli, name="prompt-cli")

if __name__ == "__main__":
    cli()