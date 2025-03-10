import os
import importlib.util
import json
from typing import Dict, Any, Tuple, Optional
import time

from core.logger import Logger
from core.utils import load_prompt

class Orchestrator:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    def _load_agent_module(self, agent_name: str) -> Optional[Any]:
        """Dynamically load the agent module."""
        agent_path = os.path.join(self.base_path, "agents", agent_name, "agent.py")
        
        if not os.path.exists(agent_path):
            return None
            
        spec = importlib.util.spec_from_file_location(f"{agent_name}_agent", agent_path)
        if not spec or not spec.loader:
            return None
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return module
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load the agent configuration."""
        with open(config_path, "r") as f:
            return json.load(f)
            
    def validate_agent(self, agent_name: str, config_path: str) -> Tuple[bool, str]:
        """Validate an agent without running it."""
        # Check if agent exists
        agent_dir = os.path.join(self.base_path, "agents", agent_name)
        if not os.path.exists(agent_dir):
            return False, f"Agent directory '{agent_name}' does not exist"
            
        # Check if agent.py exists
        agent_file = os.path.join(agent_dir, "agent.py")
        if not os.path.exists(agent_file):
            return False, f"Agent file '{agent_file}' does not exist"
            
        # Check if agent.md exists
        agent_md = os.path.join(agent_dir, "agent.md")
        if not os.path.exists(agent_md):
            return False, f"Agent documentation '{agent_md}' does not exist"
            
        # Check if config exists
        if not os.path.exists(config_path):
            return False, f"Config file '{config_path}' does not exist"
            
        # Try to load config
        try:
            config = self._load_config(config_path)
        except json.JSONDecodeError:
            return False, f"Config file '{config_path}' is not valid JSON"
            
        # Check if prompts directory exists
        prompts_dir = os.path.join(agent_dir, "prompts")
        if not os.path.exists(prompts_dir):
            return False, f"Prompts directory '{prompts_dir}' does not exist"
            
        # Try to load the agent module
        module = self._load_agent_module(agent_name)
        if not module:
            return False, f"Failed to load agent module '{agent_name}'"
            
        # Check if Agent class exists
        if not hasattr(module, "Agent"):
            return False, f"Agent module '{agent_name}' does not have an Agent class"
            
        # Check if run method exists
        try:
            agent = module.Agent(config_path)
            if not hasattr(agent, "run") or not callable(getattr(agent, "run")):
                return False, f"Agent '{agent_name}' does not have a run method"
        except Exception as e:
            return False, f"Failed to initialize agent: {str(e)}"
            
        return True, "Agent is valid"
        
    def run_agent(self, agent_name: str, config_path: str, job_id: str) -> Dict[str, Any]:
        """Run an agent with the given configuration."""
        # Validate the agent first
        is_valid, message = self.validate_agent(agent_name, config_path)
        if not is_valid:
            return {"status": "failed", "error": message}
            
        # Load the agent module
        module = self._load_agent_module(agent_name)
        if not module:
            return {"status": "failed", "error": f"Failed to load agent module '{agent_name}'"}
            
        # Load the configuration
        config = self._load_config(config_path)
        
        # Initialize the logger
        logger = Logger(job_id, agent_name)
        
        # Get prompt snapshot if specified in config
        prompt_snapshot = None
        if "prompt_file" in config:
            try:
                prompt_version = config.get("prompt_version", "latest")
                prompt_snapshot = load_prompt(
                    self.base_path, 
                    f"agents/{agent_name}/prompts/{config['prompt_file']}", 
                    prompt_version
                )
            except Exception as e:
                return {"status": "failed", "error": f"Failed to load prompt: {str(e)}"}
        
        try:
            # Initialize the agent
            agent = module.Agent(config_path)
            
            # Run the agent
            start_time = time.time()
            result = agent.run({})
            end_time = time.time()
            
            # Log metrics
            logger.log_metric("execution_time", end_time - start_time)
            
            # Write log and results
            logger.write_log("completed", config, prompt_snapshot)
            logger.write_results(result)
            
            return {"status": "completed", "result": result}
        except Exception as e:
            logger.write_log("failed", config, prompt_snapshot)
            return {"status": "failed", "error": str(e)}