#!/usr/bin/env python3
"""
Script to demonstrate loading the required packages.
"""
import os
import pandas as pd
import requests
from dotenv import load_dotenv

def main():
    """Main function to demonstrate package loading."""
    print("Successfully loaded packages:")
    
    # Pandas
    print(f"- pandas {pd.__version__}")
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    print(f"  Sample DataFrame:\n{df}")
    
    # Requests
    print(f"- requests {requests.__version__}")
    response = requests.get("https://httpbin.org/status/200")
    print(f"  HTTP Status: {response.status_code}")
    
    # python-dotenv
    print("- python-dotenv")
    # Create a temporary .env file
    with open(".env.temp", "w") as f:
        f.write("TEST_VAR=Hello from dotenv!")
    
    # Load the .env file
    load_dotenv(".env.temp")
    env_var = os.getenv("TEST_VAR")
    print(f"  Environment variable: {env_var}")
    
    # Clean up
    os.remove(".env.temp")

if __name__ == "__main__":
    main() 