import os
from typing import Optional
from git import Repo

def load_prompt(repo_path: str, file_name: str, version_tag: str = "latest") -> str:
    """
    Load a prompt file from a specific version in the git repository.
    
    Args:
        repo_path: Path to the repository
        file_name: Path to the prompt file relative to the repository root
        version_tag: Git tag to use (default: "latest" for the most recent tag)
        
    Returns:
        The prompt content as a string
    """
    repo = Repo(repo_path)
    
    # If version_tag is "latest", find the most recent tag for this file
    if version_tag == "latest":
        file_prefix = file_name.replace("/", "_").replace(".", "_")
        tags = [t.name for t in repo.tags if t.name.startswith(file_prefix)]
        if not tags:
            raise ValueError(f"No tags found for {file_name}")
        
        # Sort tags by semantic version (assuming format: file_name/vX.Y.Z)
        version_tag = sorted(tags, key=lambda x: [int(n) for n in x.split('/')[-1][1:].split('.')], reverse=True)[0]
        
    # Get the prompt content from the specified tag
    try:
        prompt = repo.git.show(f"{version_tag}:{file_name}")
        return prompt
    except Exception as e:
        raise ValueError(f"Failed to load prompt {file_name} at version {version_tag}: {str(e)}")
        
def get_repo_root() -> str:
    """Get the root directory of the git repository."""
    try:
        repo = Repo(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), search_parent_directories=True)
        return repo.working_dir
    except Exception:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))