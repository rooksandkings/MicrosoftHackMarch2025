#!/bin/bash
# Azure ML Setup Script (Final Version)
# ------------------------------------
# This script sets up the Azure ML project with minimal dependencies

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

# 5. Create a zip file of the data
echo "Creating zip package of the codebase..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ZIP_FILE="codebase_$TIMESTAMP.zip"
zip -r $ZIP_FILE *.py requirements.txt *.csv *.db .env

echo "Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Download the zip file from: $ZIP_FILE"
echo "2. Upload it manually to your Azure ML workspace at https://ml.azure.com"
echo "3. Connect to your compute instance 'Hackathon2025Compute'"
echo "4. Extract the zip file in your compute instance"
echo "5. Manually add the database connection string to Key Vault via Azure Portal:"
echo "   - Navigate to Key Vault 'kv-hackatho997940562190'"
echo "   - Add secret named 'DB-CONNECTION-STRING' with value 'sqlite:///mckinsey_data.db'"
echo "6. Run the test_connection.py script to verify database connectivity"
echo ""
echo "For more information, visit: https://portal.azure.com/" 