#!/bin/bash
# Azure ML Setup Script
# --------------------
# This script sets up the Azure ML project with the necessary components

set -e

echo "Setting up Azure ML project..."

# Variables
WORKSPACE_NAME="hackathon2025_beta"
RESOURCE_GROUP="resourceGroupHackathon"
COMPUTE_NAME="Hackathon2025Compute"  # Using the existing compute instance
KEYVAULT_NAME="kv-hackatho997940562190"  # Using existing Key Vault from the output

# 1. Install required Python packages
echo "Installing required Python packages..."
python3 -m pip install -r requirements.txt

# 2. Verify Azure ML workspace
echo "Verifying Azure ML workspace..."
az ml workspace show --name $WORKSPACE_NAME --resource-group $RESOURCE_GROUP

# 3. Verify compute instance exists
echo "Verifying compute instance..."
COMPUTE_EXISTS=$(az ml compute list --workspace-name $WORKSPACE_NAME --resource-group $RESOURCE_GROUP --query "[?name=='$COMPUTE_NAME'].name" -o tsv)

if [ -z "$COMPUTE_EXISTS" ]; then
    echo "ERROR: Compute instance $COMPUTE_NAME does not exist."
    echo "Please verify the compute name or create it in the Azure portal."
    exit 1
else
    echo "Found existing compute instance: $COMPUTE_NAME"
fi

# 4. Set up database connection secret in Key Vault
echo "Setting up database connection string in Key Vault..."
DB_CONNECTION="sqlite:///mckinsey_data.db"
az keyvault secret set --vault-name $KEYVAULT_NAME \
                      --name "DB-CONNECTION-STRING" \
                      --value "$DB_CONNECTION"

# 5. Upload codebase to Azure ML workspace
echo "Uploading codebase to Azure ML workspace..."
mkdir -p ./azureml_upload
cp -r *.py requirements.txt *.csv *.db ./azureml_upload/

# Create a zip file of the data
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ZIP_FILE="codebase_$TIMESTAMP.zip"
(cd ./azureml_upload && zip -r ../$ZIP_FILE .)

# Create a datastore folder for uploads
az ml datastore file-upload --name workspaceblobstore \
                          --workspace-name $WORKSPACE_NAME \
                          --resource-group $RESOURCE_GROUP \
                          --src-path $ZIP_FILE \
                          --target-path codebase

echo "Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Connect to your compute instance using VS Code or Jupyter"
echo "2. Download and extract the codebase from the datastore"
echo "3. Use the database_utils_azure.py file for secure database access"
echo ""
echo "For more information, visit: https://portal.azure.com/" 