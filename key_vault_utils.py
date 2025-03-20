"""
Azure Key Vault Utilities
------------------------
Provides functions to securely retrieve secrets from Azure Key Vault.
"""

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_secret(secret_name):
    """Get a secret from Azure Key Vault.
    
    Args:
        secret_name (str): The name of the secret to retrieve
        
    Returns:
        str: The secret value
    """
    key_vault_name = os.environ.get("KEY_VAULT_NAME")
    kv_uri = f"https://{key_vault_name}.vault.azure.net"
    
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=kv_uri, credential=credential)
    
    return client.get_secret(secret_name).value 