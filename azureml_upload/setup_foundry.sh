#!/bin/bash
# Azure Foundry Setup Script
# --------------------------
# This script automates the setup of Azure Foundry environment for the AI project

set -e

echo "Setting up Azure Foundry environment..."

# 1. Install required Python packages
echo "Installing required Python packages..."
python3 -m pip install -r requirements.txt
python3 -m pip install azure-identity azure-keyvault-secrets

# 2. Set up Azure Foundry environment
echo "Setting up Azure Foundry environment..."
python3 azure_foundry_setup.py

# 3. Test database connection
echo "Testing database connection..."
python3 test_connection.py

echo "Setup complete!"
echo "Your AI project is now connected to Azure Foundry."
echo ""
echo "Next steps:"
echo "1. Make sure your API key is properly set in the .env file"
echo "2. Connect to your VS Code container in Azure Foundry"
echo "3. Develop and deploy your AI models"
echo ""
echo "For more information, visit: https://portal.foundry.azure.com" 