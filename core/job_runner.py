import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import threading
import queue

from core.logger import Logger
from core.orchestrator import Orchestrator

class JobRunner:
    """
    A utility for running jobs in the background.
    This allows for asynchronous execution of agents.
    """
    def __init__(self):
        self.jobs = {}
        self.job_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        
    def submit_job(self, agent_name: str, config_path: str, 
                  input_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Submit a job to be run in the background.
        
        Args:
            agent_name: The name of the agent to run
            config_path: Path to the agent configuration
            input_params: Optional parameters to pass to the agent
            
        Returns:
            A job ID for tracking the job
        """
        if input_params is None:
            input_params = {}
            
        # Create a job ID
        job_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Record the job
        self.jobs[job_id] = {
            "agent_name": agent_name,
            "config_path": config_path,
            "input_params": input_params,
            "status": "pending",
            "submit_time": datetime.now().isoformat()
        }
        
        # Add to the queue
        self.job_queue.put((job_id, agent_name, config_path, input_params))
        
        return job_id
        
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a job.
        
        Args:
            job_id: The ID of the job to check
            
        Returns:
            A dictionary with job status information
        """
        if job_id not in self.jobs:
            return {"error": f"Job ID {job_id} not found"}
            
        return self.jobs[job_id]
        
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """
        Get a list of all jobs.
        
        Returns:
            A list of job status dictionaries
        """
        return [
            {"job_id": job_id, **job_info}
            for job_id, job_info in self.jobs.items()
        ]
        
    def _worker(self):
        """Worker thread that processes jobs from the queue."""
        while True:
            try:
                # Get a job from the queue
                job_id, agent_name, config_path, input_params = self.job_queue.get()
                
                # Update status
                self.jobs[job_id]["status"] = "running"
                self.jobs[job_id]["start_time"] = datetime.now().isoformat()
                
                # Run the job
                try:
                    orchestrator = Orchestrator()
                    result = orchestrator.run_agent(agent_name, config_path, job_id)
                    
                    # Update status
                    self.jobs[job_id]["status"] = result.get("status", "completed")
                    self.jobs[job_id]["end_time"] = datetime.now().isoformat()
                    if "error" in result:
                        self.jobs[job_id]["error"] = result["error"]
                except Exception as e:
                    # Handle exceptions
                    self.jobs[job_id]["status"] = "failed"
                    self.jobs[job_id]["error"] = str(e)
                    self.jobs[job_id]["end_time"] = datetime.now().isoformat()
                
                # Mark the task as done
                self.job_queue.task_done()
            except Exception as e:
                # Ensure the worker keeps running even if there's an error
                print(f"Error in job runner worker: {str(e)}", file=sys.stderr)
                time.sleep(1)  # Avoid spinning too fast on repeated errors
                
# Create a global instance
job_runner = JobRunner()