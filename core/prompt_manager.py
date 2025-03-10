#!/usr/bin/env python3
import os
import sys
import re
import click
from git import Repo
import subprocess
from pathlib import Path

class PromptManager:
    def __init__(self):
        self.repo = self._get_repo()
        
    def _get_repo(self):
        """Get the git repository."""
        try:
            return Repo(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        except Exception as e:
            click.echo(f"Error: Not a git repository: {str(e)}")
            sys.exit(1)
            
    def _validate_tag_format(self, tag: str) -> bool:
        """Validate that the tag follows the prompt_name/vX.Y.Z format."""
        pattern = r'^[a-zA-Z0-9_.-]+/v\d+\.\d+\.\d+$'
        return bool(re.match(pattern, tag))
        
    def _validate_file_exists(self, file_path: str) -> bool:
        """Validate that the file exists."""
        return os.path.isfile(file_path)
        
    def _is_single_file_change(self, file_path: str) -> bool:
        """Check if only a single file is being changed."""
        status = self.repo.git.status("--porcelain")
        changed_files = [line[3:] for line in status.splitlines() if line[0:2] != "??"]
        return len(changed_files) == 1 and changed_files[0] == file_path
        
    def commit_prompt(self, file_path: str, tag: str, message: str) -> bool:
        """Commit a prompt file with a specific tag."""
        # Validate file exists
        if not self._validate_file_exists(file_path):
            click.echo(f"Error: File {file_path} does not exist")
            return False
            
        # Validate tag format
        if not self._validate_tag_format(tag):
            click.echo(f"Error: Tag {tag} does not follow the required format (prompt_name/vX.Y.Z)")
            return False
            
        # Check if only this file is being changed
        if not self._is_single_file_change(file_path):
            click.echo("Error: Only a single prompt file can be committed at a time")
            return False
            
        # Commit the file
        try:
            self.repo.git.add(file_path)
            self.repo.git.commit("-m", message)
            self.repo.git.tag(tag)
            click.echo(f"Successfully committed {file_path} with tag {tag}")
            return True
        except Exception as e:
            click.echo(f"Error committing prompt: {str(e)}")
            return False
            
    def list_tags(self, prompt_name: str = None) -> list:
        """List all tags for a specific prompt or all prompts."""
        tags = [tag.name for tag in self.repo.tags]
        
        if prompt_name:
            tags = [tag for tag in tags if tag.startswith(f"{prompt_name}/")]
            
        return tags
        
    def get_history(self, file_path: str) -> list:
        """Get the commit history for a specific file."""
        if not self._validate_file_exists(file_path):
            click.echo(f"Error: File {file_path} does not exist")
            return []
            
        try:
            logs = self.repo.git.log("--pretty=format:%h|%an|%ad|%s", "--date=short", file_path).splitlines()
            return [log.split("|") for log in logs]
        except Exception as e:
            click.echo(f"Error getting history: {str(e)}")
            return []

@click.group()
def cli():
    """Prompt versioning management tool."""
    pass

@cli.command("commit")
@click.argument("prompt_file")
@click.option("--tag", required=True, help="Tag in format prompt_name/vX.Y.Z")
@click.option("--message", required=True, help="Commit message")
def commit(prompt_file, tag, message):
    """Commit a prompt file with a specific tag."""
    manager = PromptManager()
    success = manager.commit_prompt(prompt_file, tag, message)
    sys.exit(0 if success else 1)

@cli.command("list-tags")
@click.argument("prompt_name", required=False)
def list_tags(prompt_name):
    """List all tags for a specific prompt or all prompts."""
    manager = PromptManager()
    tags = manager.list_tags(prompt_name)
    for tag in tags:
        click.echo(tag)

@cli.command("history")
@click.argument("prompt_file")
def history(prompt_file):
    """Get the commit history for a specific file."""
    manager = PromptManager()
    history = manager.get_history(prompt_file)
    for commit in history:
        if len(commit) >= 4:
            click.echo(f"{commit[0]} | {commit[1]} | {commit[2]} | {commit[3]}")

if __name__ == "__main__":
    cli()