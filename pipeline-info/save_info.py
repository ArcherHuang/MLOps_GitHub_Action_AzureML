# Parameters: 
# 1: Commit SHA
# 2: SUBSCRIPTION_ID
# 3: resource_group
# 4: workspace_name
# 5: IOT_HUB_CONNECTION_STRING
# 6: GITHUB_REPOSITORY
# 7: COMMIT_URL
# 8: COMMITTER
# 9: COMMIT_TIMESTAMP
# 10: COMMIT_MESSAGE
# 11: GITHUB_WORKFLOW
# 12: GITHUB_ACTION_RUN_ID
# 13: GITHUB_ACTION_RUN_NUMBER
# 14: TEAMS_WEBHOOK

import sys
from azureml.core import Workspace

print(f"Commit ID: {sys.argv[1]}")
print(f"SUBSCRIPTION_ID: {sys.argv[2]}")
print(f"resource_group: {sys.argv[3]}")
print(f"workspace_name: {sys.argv[4]}")
print(f"IOT_HUB_CONNECTION_STRING: {sys.argv[5]}")
print(f"GITHUB_REPOSITORY: {sys.argv[6]}")
print(f"COMMIT_URL: {sys.argv[7]}")
print(f"COMMITTER: {sys.argv[8]}")
print(f"COMMIT_TIMESTAMP: {sys.argv[9]}")
print(f"COMMIT_MESSAGE: {sys.argv[10]}")
print(f"GITHUB_WORKFLOW: {sys.argv[11]}")
print(f"GITHUB_ACTION_RUN_ID: {sys.argv[12]}")
print(f"GITHUB_ACTION_RUN_NUMBER: {sys.argv[13]}")
print(f"TEAMS_WEBHOOK: {sys.argv[14]}")

# 設定 IoT Hub Device ID & blob base url
IOT_HUB_DEVICE_ID = "device01"
BLOB_MODEL_BASE_URL = "https://irisblobs.blob.core.windows.net/models"

# 設定 Workspace
workspace = Workspace(
    subscription_id = sys.argv[2],
    resource_group = sys.argv[3],
    workspace_name = sys.argv[4],
)

# 設定 AzureML Secret 供 Pipeline 使用
keyvault = workspace.get_default_keyvault()
keyvault.set_secret(name="commit-sha", value = sys.argv[1])
keyvault.set_secret(name="iot-hub-connection-string", value = sys.argv[5])
keyvault.set_secret(name="github-repository", value = sys.argv[6])
keyvault.set_secret(name="commit-url", value = sys.argv[7])
keyvault.set_secret(name="committer", value = sys.argv[8])
keyvault.set_secret(name="commit-timestamp", value = sys.argv[9])
keyvault.set_secret(name="commit-message", value = sys.argv[10])
keyvault.set_secret(name="github-workflow", value = sys.argv[11])
keyvault.set_secret(name="github-action-run-id", value = sys.argv[12])
keyvault.set_secret(name="github-action-run-number", value = sys.argv[13])
keyvault.set_secret(name="teams-webhook", value = sys.argv[14])
keyvault.set_secret(name="iot-hub-device-id", value = IOT_HUB_DEVICE_ID)
keyvault.set_secret(name="blob-model-base-url", value = BLOB_MODEL_BASE_URL)

print(f"list secret: {keyvault.list_secrets()}")
