#!/bin/bash
# Azure ML Setup Script (Without Key Vault Access)
# ------------------------------------------------
# This script sets up the Azure ML project without requiring Key Vault permissions

set -e

echo "Setting up Azure ML project..."

# Variables
WORKSPACE_NAME="hackathon2025_beta"
RESOURCE_GROUP="resourceGroupHackathon"
COMPUTE_NAME="Hackathon2025Compute"  # Using the existing compute instance

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

# 4. Create a .env file to store the connection string locally
echo "Creating .env file with database connection string..."
cat > .env << EOF
# Database configuration - will be manually added to Key Vault in the compute instance
DB_CONNECTION_STRING=sqlite:///mckinsey_data.db
EOF

# 5. Upload codebase to Azure ML workspace
echo "Uploading codebase to Azure ML workspace..."
mkdir -p ./azureml_upload
cp -r *.py requirements.txt *.csv *.db .env ./azureml_upload/

# Create a zip file of the data
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ZIP_FILE="codebase_$TIMESTAMP.zip"
(cd ./azureml_upload && zip -r ../$ZIP_FILE .)

# Upload to datastore
echo "Uploading code to datastore..."
az ml datastore file-upload --name workspaceblobstore \
                          --workspace-name $WORKSPACE_NAME \
                          --resource-group $RESOURCE_GROUP \
                          --src-path $ZIP_FILE \
                          --target-path codebase

echo "Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Connect to your compute instance at https://ml.azure.com"
echo "2. Download the codebase from the workspace datastore"
echo "3. Manually add the database connection string to Key Vault:"
echo "   - Navigate to Key Vault 'kv-hackatho997940562190' in Azure Portal"
echo "   - Add secret named 'DB-CONNECTION-STRING' with value 'sqlite:///mckinsey_data.db'"
echo "4. Run the test_connection.py script to verify database connectivity"
echo ""
echo "For more information, visit: https://portal.azure.com/" 