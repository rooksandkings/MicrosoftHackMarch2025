#!/usr/bin/env python3
"""
Azure Foundry Setup Script
--------------------------
This script securely connects to Azure Foundry using the API key stored in .env file
and sets up the necessary components for the AI project.
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AzureFoundryClient:
    def __init__(self):
        self.api_key = os.getenv("AZURE_FOUNDRY_API_KEY")
        if not self.api_key or self.api_key == "your_api_key_here":
            print("Error: Please update the AZURE_FOUNDRY_API_KEY in your .env file.")
            sys.exit(1)
        
        # Updated API endpoint to use Azure AI Studio API
        self.base_url = "https://api.studio.microsoft.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def check_project_exists(self, project_name="hackathon2025_beta"):
        """Check if the specified project exists in Azure Foundry."""
        try:
            print(f"Trying to connect to {self.base_url}/projects")
            response = requests.get(
                f"{self.base_url}/projects",
                headers=self.headers
            )
            response.raise_for_status()
            
            projects = response.json().get("projects", [])
            for project in projects:
                if project.get("name") == project_name:
                    return True, project
            
            return False, None
        except requests.exceptions.RequestException as e:
            print(f"Error checking project existence: {str(e)}")
            
            # Try alternative endpoints
            alternative_endpoints = [
                "https://api.studio.azure.com/api/v1",
                "https://api.ai.azure.com/v1"
            ]
            
            for endpoint in alternative_endpoints:
                try:
                    print(f"Trying alternative endpoint: {endpoint}/projects")
                    alt_response = requests.get(
                        f"{endpoint}/projects",
                        headers=self.headers
                    )
                    alt_response.raise_for_status()
                    
                    alt_projects = alt_response.json().get("projects", [])
                    for project in alt_projects:
                        if project.get("name") == project_name:
                            self.base_url = endpoint  # Update base URL if successful
                            return True, project
                            
                    return False, None
                except requests.exceptions.RequestException as alt_e:
                    print(f"Alternative endpoint {endpoint} failed: {str(alt_e)}")
            
            return False, None
    
    def setup_compute_instance(self, project_id, compute_name="ai-project-compute"):
        """Set up a compute instance for the project."""
        try:
            compute_config = {
                "name": compute_name,
                "vm_size": "Standard_DS3_v2",
                "min_instances": 1,
                "max_instances": 1,
                "project_id": project_id
            }
            
            response = requests.post(
                f"{self.base_url}/compute",
                headers=self.headers,
                json=compute_config
            )
            response.raise_for_status()
            
            return True, response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error setting up compute instance: {str(e)}")
            return False, None
    
    def setup_key_vault(self, project_id, vault_name="ai-project-kv"):
        """Set up Azure Key Vault for the project."""
        try:
            vault_config = {
                "name": vault_name,
                "project_id": project_id
            }
            
            response = requests.post(
                f"{self.base_url}/keyvaults",
                headers=self.headers,
                json=vault_config
            )
            response.raise_for_status()
            
            return True, response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error setting up Key Vault: {str(e)}")
            return False, None
    
    def add_secret_to_vault(self, vault_id, secret_name, secret_value):
        """Add a secret to the Key Vault."""
        try:
            secret_config = {
                "name": secret_name,
                "value": secret_value
            }
            
            response = requests.post(
                f"{self.base_url}/keyvaults/{vault_id}/secrets",
                headers=self.headers,
                json=secret_config
            )
            response.raise_for_status()
            
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error adding secret to vault: {str(e)}")
            return False

def main():
    client = AzureFoundryClient()
    
    # Check if project exists
    print("Checking if project exists...")
    project_exists, project_data = client.check_project_exists()
    
    if project_exists:
        print(f"Project 'hackathon2025_beta' found with ID: {project_data['id']}")
        project_id = project_data['id']
    else:
        print("Project 'hackathon2025_beta' not found. Please create it in the Azure Foundry portal.")
        sys.exit(1)
    
    # Set up compute instance
    print("Setting up compute instance...")
    compute_success, compute_data = client.setup_compute_instance(project_id)
    
    if compute_success:
        print(f"Compute instance created successfully with ID: {compute_data['id']}")
    else:
        print("Failed to create compute instance. Continuing with other setup steps...")
    
    # Set up Key Vault
    print("Setting up Key Vault...")
    vault_success, vault_data = client.setup_key_vault(project_id)
    
    if vault_success:
        print(f"Key Vault created successfully with ID: {vault_data['id']}")
        vault_id = vault_data['id']
        
        # Add database connection string to vault
        db_conn_string = os.getenv("DB_CONNECTION_STRING")
        if client.add_secret_to_vault(vault_id, "DB-CONNECTION-STRING", db_conn_string):
            print("Database connection string added to Key Vault successfully.")
        else:
            print("Failed to add database connection string to Key Vault.")
    else:
        print("Failed to create Key Vault. Cannot add secrets.")
    
    print("\nSetup process completed. Next steps:")
    print("1. Connect to your compute instance via VS Code using Azure Foundry extension")
    print("2. Upload your codebase to the compute instance")
    print("3. Update your database_utils.py to use Key Vault for credentials")
    print("4. Run test scripts to verify connectivity")

if __name__ == "__main__":
    main() 