#!/usr/bin/env python
# Sample script to run the email summary agent

import os
import sys
from unittest.mock import patch
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock the API keys
os.environ["OPENAI_API_KEY"] = "mock-key"
os.environ["SALESFORCE_API_KEY"] = "mock-key"

from agents.email_summary_agent.agent import Agent

# Initialize the agent
config_path = "./agents/email_summary_agent/config.json"
agent = Agent(config_path)

# Run the agent with a mock account ID
with patch("adapters.crm.salesforce_adapter.SalesforceAdapter.fetch_data") as mock_fetch:
    # Mock the CRM response
    mock_fetch.return_value = {
        "success": True,
        "data": {
            "id": "acc-test",
            "name": "Test Company",
            "industry": "Technology",
            "website": "https://test.com",
            "annual_revenue": 5000000
        }
    }
    
    # Run the agent
    result = agent.run({"account_id": "acc-test"})
    
    # Print the result
    print("Agent Result:")
    print(json.dumps(result, indent=2))