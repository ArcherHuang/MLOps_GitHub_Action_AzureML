# Parameters: 
# $1: resource-group
# $2: region
# $3: workspace-name

az extension add -n ml -y

echo "resource-group: $1"
echo "region: $2"
echo "workspace-name: $3"

RESOURCE_GROUP_NAME=${RESOURCE_GROUP_NAME:-}
if [[ -z "$RESOURCE_GROUP_NAME" ]]
then
    echo "No resource group name [RESOURCE_GROUP_NAME] specified, defaulting to $1."
    az configure --defaults group=$1 workspace=$3 location=$2
    echo "Default resource group set to $1"
else
    echo "Workflows are using the new subscription."
fi