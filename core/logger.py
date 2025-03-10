import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import git

class Logger:
    def __init__(self, job_id: str, agent_name: str):
        self.job_id = job_id
        self.agent_name = agent_name
        self.start_time = time.time()
        self.metrics = {
            "llm_latency_seconds": 0,
            "tokens_used": 0,
            "api_call_counts": {}
        }
        self.log_path = Path("storage/logs")
        self.log_path.mkdir(parents=True, exist_ok=True)
        self.results_path = Path("storage/job_results")
        self.results_path.mkdir(parents=True, exist_ok=True)
        
    def log_metric(self, metric_name: str, value: Any):
        """Log a metric value."""
        if metric_name.startswith("api_call_"):
            api_name = metric_name.replace("api_call_", "")
            if api_name not in self.metrics["api_call_counts"]:
                self.metrics["api_call_counts"][api_name] = 0
            self.metrics["api_call_counts"][api_name] += int(value)
        else:
            self.metrics[metric_name] = value
    
    def _get_git_commit_hash(self) -> Optional[str]:
        """Get the current git commit hash."""
        try:
            repo = git.Repo(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            return repo.head.commit.hexsha
        except (git.InvalidGitRepositoryError, git.NoSuchPathError):
            return None
            
    def write_log(self, status: str, config_snapshot: Dict[str, Any], prompt_snapshot: Optional[str] = None):
        """Write job log to file."""
        log_data = {
            "job_id": self.job_id,
            "agent": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "config_snapshot": config_snapshot,
            "metrics": self.metrics,
            "status": status,
            "git_commit_hash": self._get_git_commit_hash()
        }
        
        if prompt_snapshot:
            log_data["prompt_snapshot"] = prompt_snapshot
            
        log_file = self.log_path / f"{self.job_id}.json"
        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=2)
            
    def write_results(self, results: Dict[str, Any]):
        """Write job results to file."""
        results_file = self.results_path / f"{self.job_id}_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)