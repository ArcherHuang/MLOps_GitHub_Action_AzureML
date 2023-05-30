# Azure Blob > AzureML Datastores > AzureML Data assets

# Parameters: 
#   sys.argv[1]: BLOB SECRET
#   sys.argv[2]: Subscription ID
#   sys.argv[3]: Resource Group
#   sys.argv[4]: Workspace Name

import sys
from azureml.core import Workspace
from azureml.core import Dataset
from azureml.core import Datastore
from azureml.data.datapath import DataPath, DataPathComputeBinding

# 設定 Azure Blob 相關資訊
blob_datasets = ['train', 'test']
blob_train_dataset_datetime = "20230530_073041"
blob_test_dataset_datetime = "20230530_073041"
blob_account_name = "irisblobs"
datasets_container_name = "datasets"

# 設定 Workspace
workspace = Workspace(
    subscription_id = sys.argv[2],
    resource_group = sys.argv[3],
    workspace_name = sys.argv[4],
)

# 取得 Blob Key
keyvault = workspace.get_default_keyvault()
retrieved_secret = keyvault.get_secret(name="blob-account-key")

# 連接已有的 Blob Datasets
for dataset_name in blob_datasets:
    azureml_datastore_name = ""
    blob_path = ""
    if dataset_name == 'train':
        azureml_datastore_name = f"irissamples_{dataset_name}_{blob_train_dataset_datetime}"
        blob_path = f"Training/{blob_train_dataset_datetime}/*"
    else:
        azureml_datastore_name = f"irissamples_{dataset_name}_{blob_test_dataset_datetime}"
        blob_path = f"Test/{blob_test_dataset_datetime}/*"

    # 將 AzureML 的 Datastore 與 Azure Blob 連結
    Datastore.register_azure_blob_container(workspace = workspace, 
                                                            datastore_name = azureml_datastore_name, 
                                                            container_name = datasets_container_name, 
                                                            account_name = blob_account_name,
                                                            account_key = retrieved_secret)

    # 註冊 AzureML Data assets
    iris_azureml_datastore_path = [
        DataPath(
            Datastore.get(workspace, azureml_datastore_name),
            blob_path
        )
    ]
    iris_azureml_ds = Dataset.File.from_files(path=iris_azureml_datastore_path)
    iris_azureml_ds.register(workspace, f"Iris{dataset_name.title()}FileData", create_new_version=True)
