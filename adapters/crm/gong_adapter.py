import os
import time
from typing import Dict, Any, List, Optional
import json
import random
from datetime import datetime, timedelta

class GongAdapter:
    def __init__(self):
        self.api_key = os.getenv("GONG_API_KEY")
        if not self.api_key:
            raise ValueError("Gong API key is missing. Set the GONG_API_KEY environment variable.")
            
    def fetch_data(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch data from Gong based on the query.
        
        Args:
            query: A dictionary with query parameters, e.g. {"type": "call", "id": "123"}
            
        Returns:
            The retrieved data as a dictionary
        """
        # In a real implementation, this would make an API call to Gong
        # For this example, we'll simulate a response
        
        start_time = time.time()
        
        # Simulate API latency
        time.sleep(0.4)
        
        # Mock response based on query type
        response = {"success": True}
        
        if query.get("type") == "call":
            call_date = datetime.now() - timedelta(days=random.randint(1, 30))
            
            response["data"] = {
                "id": query.get("id", f"call-{random.randint(1000, 9999)}"),
                "title": "Sales Demo Call",
                "date": call_date.strftime("%Y-%m-%d"),
                "duration_minutes": random.randint(15, 60),
                "participants": [
                    {
                        "name": "Sales Rep",
                        "email": "sales@ourcompany.com",
                        "company": "Our Company",
                        "speaker_id": "speaker-1"
                    },
                    {
                        "name": "Prospect",
                        "email": "prospect@client.com",
                        "company": "Client Company",
                        "speaker_id": "speaker-2"
                    }
                ],
                "topics": [
                    {"name": "Pricing", "mentions": random.randint(1, 10)},
                    {"name": "Competition", "mentions": random.randint(1, 5)},
                    {"name": "Integration", "mentions": random.randint(1, 8)}
                ],
                "transcript": self._generate_mock_transcript()
            }
        elif query.get("type") == "user":
            response["data"] = {
                "id": query.get("id", f"user-{random.randint(1000, 9999)}"),
                "name": "Jane Smith",
                "email": "jane.smith@ourcompany.com",
                "title": "Account Executive",
                "call_stats": {
                    "total_calls": random.randint(50, 200),
                    "avg_duration_minutes": random.randint(20, 45),
                    "talk_ratio": random.uniform(0.4, 0.7)
                }
            }
        else:
            response["success"] = False
            response["error"] = "Invalid query type"
            
        end_time = time.time()
        response["latency"] = end_time - start_time
        
        return response
        
    def _generate_mock_transcript(self) -> List[Dict[str, Any]]:
        """Generate a mock transcript for a call."""
        transcript = []
        
        # Mock conversation snippets
        conversation = [
            {"speaker": "speaker-1", "text": "Thanks for joining the call today. I'd like to walk you through our product."},
            {"speaker": "speaker-2", "text": "I'm looking forward to it. We've been evaluating several solutions."},
            {"speaker": "speaker-1", "text": "Great! Let me start by showing you the dashboard."},
            {"speaker": "speaker-2", "text": "How does your pricing model work?"},
            {"speaker": "speaker-1", "text": "We have a subscription-based model, starting at $499 per month."},
            {"speaker": "speaker-2", "text": "How does that compare to your competitors?"},
            {"speaker": "speaker-1", "text": "We offer more features at a lower price point than most competitors."},
            {"speaker": "speaker-2", "text": "What about integration with our existing systems?"},
            {"speaker": "speaker-1", "text": "We have APIs and pre-built connectors for most major platforms."}
        ]
        
        current_time = 0
        for entry in conversation:
            duration = len(entry["text"]) // 20 + 1  # Rough estimate of seconds based on text length
            transcript.append({
                "speaker_id": entry["speaker"],
                "text": entry["text"],
                "start_time": current_time,
                "end_time": current_time + duration
            })
            current_time += duration + random.randint(1, 3)  # Add a small pause between speakers
            
        return transcript
        
    def update_data(self, data: Dict[str, Any]) -> bool:
        """
        Update data in Gong.
        
        Args:
            data: A dictionary with the data to update, must include "type" and "id"
            
        Returns:
            True if the update was successful, False otherwise
        """
        # In a real implementation, this would make an API call to Gong
        # For this example, we'll simulate a response
        
        if "type" not in data or "id" not in data:
            return False
            
        # Simulate API latency
        time.sleep(0.4)
        
        # Simulate success/failure (85% success rate)
        return random.random() < 0.85