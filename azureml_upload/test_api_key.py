#!/usr/bin/env python3
"""
Test API Key Script
------------------
Simple script to test the Azure Foundry/AI Studio API key connectivity.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_key():
    """Test the API key against multiple possible endpoints."""
    api_key = os.getenv("AZURE_FOUNDRY_API_KEY")
    if not api_key:
        print("Error: AZURE_FOUNDRY_API_KEY not found in .env file")
        return False
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        "https://api.studio.microsoft.com/api/v1",
        "https://api.studio.azure.com/api/v1",
        "https://api.ai.azure.com/v1",
        "https://api.aistudio.microsoft.com/api/v1",
        "https://api.aistudio.azure.com/api/v1"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        try:
            response = requests.get(
                f"{endpoint}/projects",
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"SUCCESS! Connection established to {endpoint}")
                print(f"Status Code: {response.status_code}")
                try:
                    projects = response.json().get("projects", [])
                    print(f"Projects found: {len(projects)}")
                    for project in projects:
                        print(f"  - {project.get('name', 'Unnamed project')}")
                except Exception as e:
                    print(f"Could not parse projects: {str(e)}")
                
                return True
            else:
                print(f"Failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {str(e)}")
    
    print("\nAll endpoints failed. Please check your API key and network connectivity.")
    return False

if __name__ == "__main__":
    print("Testing Azure Foundry/AI Studio API key...")
    success = test_api_key()
    sys.exit(0 if success else 1) 