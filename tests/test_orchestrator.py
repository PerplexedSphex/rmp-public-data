import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator import Orchestrator

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Orchestrator()
        
    @patch("core.orchestrator.os.path.exists")
    def test_validate_agent_missing_directory(self, mock_exists):
        """Test validation fails when agent directory does not exist."""
        # Set up mocks
        mock_exists.return_value = False
        
        # Call the method
        is_valid, message = self.orchestrator.validate_agent("nonexistent_agent", "dummy_config.json")
        
        # Check the result
        self.assertFalse(is_valid)
        self.assertIn("directory", message)
        
    @patch("core.orchestrator.os.path.exists")
    def test_validate_agent_missing_agent_file(self, mock_exists):
        """Test validation fails when agent.py file does not exist."""
        # Set up mocks
        def mock_exists_side_effect(path):
            if path.endswith("nonexistent_agent"):
                return True
            if path.endswith("agent.py"):
                return False
            return True
            
        mock_exists.side_effect = mock_exists_side_effect
        
        # Call the method
        is_valid, message = self.orchestrator.validate_agent("nonexistent_agent", "dummy_config.json")
        
        # Check the result
        self.assertFalse(is_valid)
        self.assertIn("agent file", message)
        
    @patch("core.orchestrator.os.path.exists")
    def test_validate_agent_missing_agent_md(self, mock_exists):
        """Test validation fails when agent.md file does not exist."""
        # Set up mocks
        def mock_exists_side_effect(path):
            if path.endswith("nonexistent_agent"):
                return True
            if path.endswith("agent.py"):
                return True
            if path.endswith("agent.md"):
                return False
            return True
            
        mock_exists.side_effect = mock_exists_side_effect
        
        # Call the method
        is_valid, message = self.orchestrator.validate_agent("nonexistent_agent", "dummy_config.json")
        
        # Check the result
        self.assertFalse(is_valid)
        self.assertIn("documentation", message)
        
    @patch("core.orchestrator.os.path.exists")
    @patch("core.orchestrator.Orchestrator._load_config")
    @patch("core.orchestrator.Orchestrator._load_agent_module")
    def test_validate_agent_valid(self, mock_load_module, mock_load_config, mock_exists):
        """Test validation succeeds for a valid agent."""
        # Set up mocks
        mock_exists.return_value = True
        mock_load_config.return_value = {"name": "test_agent"}
        
        # Mock the agent module
        mock_agent = MagicMock()
        mock_agent.run = MagicMock()
        mock_agent_class = MagicMock(return_value=mock_agent)
        
        mock_module = MagicMock()
        mock_module.Agent = mock_agent_class
        mock_load_module.return_value = mock_module
        
        # Call the method
        is_valid, message = self.orchestrator.validate_agent("test_agent", "dummy_config.json")
        
        # Check the result
        self.assertTrue(is_valid)
        self.assertIn("valid", message)
        
    @patch("core.orchestrator.Orchestrator.validate_agent")
    @patch("core.orchestrator.Orchestrator._load_agent_module")
    @patch("core.orchestrator.Orchestrator._load_config")
    @patch("core.orchestrator.Logger")
    def test_run_agent(self, mock_logger, mock_load_config, mock_load_module, mock_validate):
        """Test running an agent."""
        # Set up mocks
        mock_validate.return_value = (True, "Agent is valid")
        mock_load_config.return_value = {"name": "test_agent"}
        
        # Mock the logger
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        
        # Mock the agent module
        mock_agent = MagicMock()
        mock_agent.run.return_value = {"result": "success"}
        mock_agent_class = MagicMock(return_value=mock_agent)
        
        mock_module = MagicMock()
        mock_module.Agent = mock_agent_class
        mock_load_module.return_value = mock_module
        
        # Call the method
        result = self.orchestrator.run_agent("test_agent", "dummy_config.json", "job-123")
        
        # Check the result
        self.assertEqual(result.get("status"), "completed")
        self.assertEqual(result.get("result", {}).get("result"), "success")
        
        # Verify the agent was initialized and run
        mock_agent_class.assert_called_once_with("dummy_config.json")
        mock_agent.run.assert_called_once()
        
        # Verify the logger was used
        mock_logger_instance.log_metric.assert_called()
        mock_logger_instance.write_log.assert_called_with("completed", {"name": "test_agent"}, None)
        mock_logger_instance.write_results.assert_called_with({"result": "success"})
        
if __name__ == "__main__":
    unittest.main()