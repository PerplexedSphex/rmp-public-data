import os
import json
from typing import Dict, Any

# Import adapters
from adapters.llm.openai_adapter import OpenAIAdapter
from adapters.crm.salesforce_adapter import SalesforceAdapter
from core.utils import load_prompt
from core.logger import Logger

class Agent:
    def __init__(self, config_path: str):
        # Load configuration
        with open(config_path, "r") as f:
            self.config = json.load(f)
        
        # Initialize adapters
        self.llm_adapter = OpenAIAdapter()
        self.crm_adapter = SalesforceAdapter()
        
    def run(self, input_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the email summary agent.
        
        Args:
            input_params: A dictionary with input parameters
            
        Returns:
            A dictionary with the agent results
        """
        # Set defaults for input parameters
        account_id = input_params.get("account_id", self.config.get("default_account_id"))
        
        # Fetch account data from CRM
        account_data = self._fetch_account_data(account_id)
        if not account_data:
            return {
                "success": False,
                "error": f"Failed to fetch account data for ID: {account_id}"
            }
        
        # Summarize the account data
        summary = self._generate_summary(account_data)
        
        return {
            "success": True,
            "account_id": account_id,
            "account_name": account_data.get("name", "Unknown"),
            "summary": summary
        }
        
    def _fetch_account_data(self, account_id: str) -> Dict[str, Any]:
        """Fetch account data from CRM."""
        response = self.crm_adapter.fetch_data({
            "type": "account",
            "id": account_id
        })
        
        if not response.get("success", False):
            return {}
            
        return response.get("data", {})
        
    def _generate_summary(self, account_data: Dict[str, Any]) -> str:
        """Generate a summary using the LLM."""
        # In a real implementation, you would:
        # 1. Load the prompt template
        # 2. Fill in the template with account data
        # 3. Send the prompt to the LLM
        
        prompt = f"""
        Summarize the following account information:
        
        Account Name: {account_data.get('name', 'Unknown')}
        Industry: {account_data.get('industry', 'Unknown')}
        Website: {account_data.get('website', 'Unknown')}
        Annual Revenue: ${account_data.get('annual_revenue', 0):,.2f}
        
        Generate a concise summary of this account suitable for a sales email.
        """
        
        response = self.llm_adapter.complete(
            prompt=prompt,
            model=self.config.get("llm_model", "gpt-4"),
            temperature=self.config.get("temperature", 0.7)
        )
        
        # Extract the generated text from the LLM response
        if "choices" in response and len(response["choices"]) > 0:
            return response["choices"][0]["message"]["content"]
        else:
            return "Failed to generate summary."