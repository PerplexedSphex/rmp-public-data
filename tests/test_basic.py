import os
import sys
import unittest

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestBasic(unittest.TestCase):
    def test_project_structure(self):
        """Test that essential project directories exist."""
        # Core directories
        self.assertTrue(os.path.isdir("core"))
        self.assertTrue(os.path.isdir("agents"))
        self.assertTrue(os.path.isdir("adapters"))
        self.assertTrue(os.path.isdir("cli"))
        
        # Adapter subdirectories
        self.assertTrue(os.path.isdir("adapters/llm"))
        self.assertTrue(os.path.isdir("adapters/crm"))
        
        # Agent directories
        self.assertTrue(os.path.isdir("agents/email_summary_agent"))
        
    def test_required_files(self):
        """Test that essential files exist."""
        # Config files
        self.assertTrue(os.path.isfile("requirements.txt"))
        self.assertTrue(os.path.isfile("setup.py"))
        
        # Core files
        self.assertTrue(os.path.isfile("core/orchestrator.py"))
        self.assertTrue(os.path.isfile("core/logger.py"))
        self.assertTrue(os.path.isfile("core/utils.py"))
        self.assertTrue(os.path.isfile("core/prompt_manager.py"))
        
        # CLI files
        self.assertTrue(os.path.isfile("cli/cli.py"))
        
        # Agent files
        self.assertTrue(os.path.isfile("agents/email_summary_agent/agent.py"))
        self.assertTrue(os.path.isfile("agents/email_summary_agent/config.json"))
        
if __name__ == "__main__":
    unittest.main()