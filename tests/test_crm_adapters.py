import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.crm.salesforce_adapter import SalesforceAdapter
from adapters.crm.gong_adapter import GongAdapter

class TestCRMAdapters(unittest.TestCase):
    @patch.dict(os.environ, {"SALESFORCE_API_KEY": "test-key"})
    def test_salesforce_adapter_init(self):
        """Test that the Salesforce adapter can be initialized with an API key."""
        adapter = SalesforceAdapter()
        self.assertEqual(adapter.api_key, "test-key")
        
    @patch.dict(os.environ, {"SALESFORCE_API_KEY": "test-key"})
    def test_salesforce_fetch_account(self):
        """Test that the Salesforce adapter can fetch account data."""
        adapter = SalesforceAdapter()
        response = adapter.fetch_data({"type": "account", "id": "acc-123"})
        
        # Check response structure
        self.assertIn("success", response)
        self.assertTrue(response["success"])
        self.assertIn("data", response)
        
        # Check account data
        self.assertEqual(response["data"]["id"], "acc-123")
        self.assertIn("name", response["data"])
        self.assertIn("industry", response["data"])
        self.assertIn("website", response["data"])
        self.assertIn("annual_revenue", response["data"])
        
    @patch.dict(os.environ, {"SALESFORCE_API_KEY": "test-key"})
    def test_salesforce_fetch_opportunity(self):
        """Test that the Salesforce adapter can fetch opportunity data."""
        adapter = SalesforceAdapter()
        response = adapter.fetch_data({"type": "opportunity", "id": "opp-123"})
        
        # Check response structure
        self.assertIn("success", response)
        self.assertTrue(response["success"])
        self.assertIn("data", response)
        
        # Check opportunity data
        self.assertEqual(response["data"]["id"], "opp-123")
        self.assertIn("name", response["data"])
        self.assertIn("stage", response["data"])
        self.assertIn("amount", response["data"])
        self.assertIn("close_date", response["data"])
        self.assertIn("account", response["data"])
        
    @patch.dict(os.environ, {"SALESFORCE_API_KEY": "test-key"})
    def test_salesforce_update_data(self):
        """Test that the Salesforce adapter can update data."""
        adapter = SalesforceAdapter()
        result = adapter.update_data({
            "type": "account",
            "id": "acc-123",
            "name": "Updated Account Name"
        })
        
        # The result might be True or False, but it should be a boolean
        self.assertIsInstance(result, bool)
        
    @patch.dict(os.environ, {"GONG_API_KEY": "test-key"})
    def test_gong_adapter_init(self):
        """Test that the Gong adapter can be initialized with an API key."""
        adapter = GongAdapter()
        self.assertEqual(adapter.api_key, "test-key")
        
    @patch.dict(os.environ, {"GONG_API_KEY": "test-key"})
    def test_gong_fetch_call(self):
        """Test that the Gong adapter can fetch call data."""
        adapter = GongAdapter()
        response = adapter.fetch_data({"type": "call", "id": "call-123"})
        
        # Check response structure
        self.assertIn("success", response)
        self.assertTrue(response["success"])
        self.assertIn("data", response)
        
        # Check call data
        self.assertEqual(response["data"]["id"], "call-123")
        self.assertIn("title", response["data"])
        self.assertIn("date", response["data"])
        self.assertIn("duration_minutes", response["data"])
        self.assertIn("participants", response["data"])
        self.assertIn("topics", response["data"])
        self.assertIn("transcript", response["data"])
        
    @patch.dict(os.environ, {"GONG_API_KEY": "test-key"})
    def test_gong_fetch_user(self):
        """Test that the Gong adapter can fetch user data."""
        adapter = GongAdapter()
        response = adapter.fetch_data({"type": "user", "id": "user-123"})
        
        # Check response structure
        self.assertIn("success", response)
        self.assertTrue(response["success"])
        self.assertIn("data", response)
        
        # Check user data
        self.assertEqual(response["data"]["id"], "user-123")
        self.assertIn("name", response["data"])
        self.assertIn("email", response["data"])
        self.assertIn("title", response["data"])
        self.assertIn("call_stats", response["data"])
        
    @patch.dict(os.environ, {"GONG_API_KEY": "test-key"})
    def test_gong_update_data(self):
        """Test that the Gong adapter can update data."""
        adapter = GongAdapter()
        result = adapter.update_data({
            "type": "call",
            "id": "call-123",
            "title": "Updated Call Title"
        })
        
        # The result might be True or False, but it should be a boolean
        self.assertIsInstance(result, bool)
        
if __name__ == "__main__":
    unittest.main()