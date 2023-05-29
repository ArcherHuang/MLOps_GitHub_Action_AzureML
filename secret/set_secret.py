# Parameters: 
# 1: BLOB SECRET
# 2: Subscription_ID
# 3: resource_group
# 4: workspace_name

import sys
from azureml.core import Workspace

print(f"BLOB SECRET: {sys.argv[1]}")
print(f"Subscription_ID: {sys.argv[2]}")
print(f"resource_group: {sys.argv[3]}")
print(f"workspace_name: {sys.argv[4]}")

workspace = Workspace(
    subscription_id = sys.argv[2],
    resource_group = sys.argv[3],
    workspace_name = sys.argv[4],
)
keyvault = workspace.get_default_keyvault()
keyvault.set_secret(name="blob-account-key", value = sys.argv[1])

print(f"list secret: {keyvault.list_secrets()}")

retrieved_secret = keyvault.get_secret(name="blob-account-key")
print(f"retrieved_secret: {retrieved_secret}")