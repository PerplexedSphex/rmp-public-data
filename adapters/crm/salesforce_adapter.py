import os
import time
from typing import Dict, Any, Optional
import json
import random

class SalesforceAdapter:
    def __init__(self):
        self.api_key = os.getenv("SALESFORCE_API_KEY")
        if not self.api_key:
            raise ValueError("Salesforce API key is missing. Set the SALESFORCE_API_KEY environment variable.")
            
    def fetch_data(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch data from Salesforce based on the query.
        
        Args:
            query: A dictionary with query parameters, e.g. {"type": "opportunity", "id": "123"}
            
        Returns:
            The retrieved data as a dictionary
        """
        # In a real implementation, this would make an API call to Salesforce
        # For this example, we'll simulate a response
        
        start_time = time.time()
        
        # Simulate API latency
        time.sleep(0.3)
        
        # Mock response based on query type
        response = {"success": True}
        
        if query.get("type") == "opportunity":
            response["data"] = {
                "id": query.get("id", f"opp-{random.randint(1000, 9999)}"),
                "name": "Sample Opportunity",
                "stage": "Qualification",
                "amount": 50000.00,
                "close_date": "2025-06-30",
                "account": {
                    "id": "acc-123",
                    "name": "Sample Account"
                }
            }
        elif query.get("type") == "account":
            response["data"] = {
                "id": query.get("id", f"acc-{random.randint(1000, 9999)}"),
                "name": "Sample Account",
                "industry": "Technology",
                "website": "https://example.com",
                "annual_revenue": 10000000.00
            }
        elif query.get("type") == "contact":
            response["data"] = {
                "id": query.get("id", f"con-{random.randint(1000, 9999)}"),
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "555-123-4567",
                "title": "CTO"
            }
        else:
            response["success"] = False
            response["error"] = "Invalid query type"
            
        end_time = time.time()
        response["latency"] = end_time - start_time
        
        return response
        
    def update_data(self, data: Dict[str, Any]) -> bool:
        """
        Update data in Salesforce.
        
        Args:
            data: A dictionary with the data to update, must include "type" and "id"
            
        Returns:
            True if the update was successful, False otherwise
        """
        # In a real implementation, this would make an API call to Salesforce
        # For this example, we'll simulate a response
        
        if "type" not in data or "id" not in data:
            return False
            
        # Simulate API latency
        time.sleep(0.3)
        
        # Simulate success/failure (90% success rate)
        return random.random() < 0.9