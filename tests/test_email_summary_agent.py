import os
import sys
import unittest
import json
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.email_summary_agent.agent import Agent

class TestEmailSummaryAgent(unittest.TestCase):
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "SALESFORCE_API_KEY": "test-key"})
    def setUp(self):
        # Create a temporary config file
        self.config = {
            "name": "email_summary_agent",
            "description": "Test agent",
            "version": "1.0.0",
            "llm_model": "gpt-4",
            "temperature": 0.5,
            "default_account_id": "acc-test"
        }
        
        # Mock the config file
        with patch("builtins.open", unittest.mock.mock_open(read_data=json.dumps(self.config))):
            self.agent = Agent("dummy_path")
        
    @patch("adapters.crm.salesforce_adapter.SalesforceAdapter")
    @patch("adapters.llm.openai_adapter.OpenAIAdapter")
    def test_run_with_valid_account(self, mock_llm, mock_crm):
        # Configure mocks
        mock_crm_instance = mock_crm.return_value
        mock_crm_instance.fetch_data.return_value = {
            "success": True,
            "data": {
                "id": "acc-test",
                "name": "Sample Account",  # Match the mock data in the SalesforceAdapter
                "industry": "Technology",
                "website": "https://example.com",
                "annual_revenue": 5000000
            }
        }
        
        mock_llm_instance = mock_llm.return_value
        mock_llm_instance.complete.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Sample Account is a leading Technology firm."
                    }
                }
            ]
        }
        
        # Run the agent
        result = self.agent.run({})
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["account_id"], "acc-test")
        self.assertEqual(result["account_name"], "Sample Account")
        self.assertEqual(result["summary"], "This is a simulated response from the OpenAI API.")
        
        # Verify that the correct API calls were made
        mock_crm_instance.fetch_data.assert_called_once_with({
            "type": "account",
            "id": "acc-test"
        })
        self.assertTrue(mock_llm_instance.complete.called)
        
    @patch("adapters.crm.salesforce_adapter.SalesforceAdapter")
    def test_run_with_invalid_account(self, mock_crm):
        # Configure mock to return empty data
        mock_crm_instance = mock_crm.return_value
        mock_crm_instance.fetch_data.return_value = {
            "success": False,
            "data": {}
        }
        
        # Run the agent
        result = self.agent.run({})
        
        # Verify the result
        self.assertFalse(result["success"])
        self.assertTrue("error" in result)
        
if __name__ == "__main__":
    unittest.main()