import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.llm.openai_adapter import OpenAIAdapter
from adapters.llm.claude_adapter import ClaudeAdapter
from adapters.llm.gemini_adapter import GeminiAdapter

class TestLLMAdapters(unittest.TestCase):
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_openai_adapter_init(self):
        """Test that the OpenAI adapter can be initialized with an API key."""
        adapter = OpenAIAdapter()
        self.assertEqual(adapter.api_key, "test-key")
        
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_openai_adapter_complete(self):
        """Test that the OpenAI adapter can generate a completion."""
        adapter = OpenAIAdapter()
        response = adapter.complete("Test prompt", model="gpt-4", temperature=0.5)
        
        # Check response structure
        self.assertIn("choices", response)
        self.assertIn("usage", response)
        self.assertIn("model", response)
        
        # Check the first choice
        self.assertGreater(len(response["choices"]), 0)
        self.assertIn("message", response["choices"][0])
        self.assertIn("content", response["choices"][0]["message"])
        
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_claude_adapter_init(self):
        """Test that the Claude adapter can be initialized with an API key."""
        adapter = ClaudeAdapter()
        self.assertEqual(adapter.api_key, "test-key")
        
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_claude_adapter_complete(self):
        """Test that the Claude adapter can generate a completion."""
        adapter = ClaudeAdapter()
        response = adapter.complete("Test prompt", model="claude-3-opus-20240229", temperature=0.5)
        
        # Check response structure
        self.assertIn("content", response)
        self.assertIn("usage", response)
        self.assertIn("model", response)
        
        # Check the content
        self.assertGreater(len(response["content"]), 0)
        self.assertIn("type", response["content"][0])
        self.assertIn("text", response["content"][0])
        
    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"})
    def test_gemini_adapter_init(self):
        """Test that the Gemini adapter can be initialized with an API key."""
        adapter = GeminiAdapter()
        self.assertEqual(adapter.api_key, "test-key")
        
    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"})
    def test_gemini_adapter_complete(self):
        """Test that the Gemini adapter can generate a completion."""
        adapter = GeminiAdapter()
        response = adapter.complete("Test prompt", model="gemini-pro", temperature=0.5)
        
        # Check response structure
        self.assertIn("candidates", response)
        self.assertIn("usage_metadata", response)
        
        # Check the first candidate
        self.assertGreater(len(response["candidates"]), 0)
        self.assertIn("content", response["candidates"][0])
        self.assertIn("parts", response["candidates"][0]["content"])
        
if __name__ == "__main__":
    unittest.main()