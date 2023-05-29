import argparse
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import pandas as pd
from azureml.core import Run
from azureml.pipeline.core import PipelineData
from azureml.core import Datastore
from azureml.core import Workspace
from datetime import datetime
from azureml.core import Dataset
from azureml.core import Model
import json 
from azure.iot.hub import IoTHubRegistryManager
import teams_notify

parser = argparse.ArgumentParser()
parser.add_argument("--blob_container_name", type=str, help="output path")
parser.add_argument("--blob_account_name", type=str, help="output path")
parser.add_argument("--train_input", dest="train_input", required=True)
parser.add_argument("--test_datasets", type=str, help="output path")

args = parser.parse_args()
print(f"Argument blob_container_name: {args.blob_container_name}")
print(f"Argument blob_account_name: {args.blob_account_name}")
print(f"Argument train_input: {args.train_input}")
print(f"Argument test_datasets: {args.test_datasets}")

print(f"test_datasets: {os.listdir(args.test_datasets)}")

# 取得 Workspace
run = Run.get_context()
ws = run.experiment.workspace

# 取得 Blob Key
keyvault = ws.get_default_keyvault()
retrieved_secret = keyvault.get_secret(name="blob-account-key")

# 取得 IoT Hub Connection String
iot_hub_connection_string_secret = keyvault.get_secret(name="iot-hub-connection-string")

# 設定 Datastore
blob_datastore = Datastore.register_azure_blob_container(workspace=ws, 
                                                         datastore_name=args.blob_container_name, 
                                                         container_name=args.blob_container_name, 
                                                         account_name=args.blob_account_name,
                                                         account_key=retrieved_secret)

# 取得 OutputFileDatasetConfig 的資料
json_file = open(os.path.join(args.train_input, "OutputFileDatasetConfig-Parameter.json"))
datas = json.load(json_file)
json_file.close()
print(f"model_name: {datas['model_name']}")
print(f"file_url: {datas['file_url']}")
print(f"json_url: {datas['json_url']}")
print(f"workflow_info: {datas['workflow_info']}")
workflow_infos = datas['workflow_info']
print(f"workflow_infos: {workflow_infos}, type: {type(workflow_infos)}")
print(f"sha: {workflow_infos['commit_info']['commit_sha']}")

# 載入模型
registry_model_path = Model.get_model_path( model_name=datas['model_name'] )
print(f"registry_model_path: {registry_model_path}")
loaded_model = tf.keras.models.load_model(registry_model_path)

# 評估模型
## 讀取 CSV 檔案
test_file = f"{args.test_datasets}/iris_test.csv"
test_data = pd.read_csv(test_file, header=0)

## 擷取特徵和標籤
test_features = test_data.iloc[:, :-1].values
test_labels = test_data.iloc[:, -1].values

## 將標籤轉換為 one-hot 編碼
test_labels = tf.keras.utils.to_categorical(test_labels, num_classes=3)

loss, accuracy = loaded_model.evaluate(test_features, test_labels)
print(f"[Evaluate Step] loss: {loss}")
print(f"[Evaluate Step] accuracy: {accuracy}")

# 存放 Workflow 相關資訊
workflow_infos.update({
    "evaluate_info": {
        "train_loss": loss,
        "accuracy": accuracy
    }
})
print(f"workflow_infos: {workflow_infos}")

json_object = json.dumps(workflow_infos)
print(json_object)
json_file_name = f"{workflow_infos['commit_info']['commit_sha']}.json"
print(f"json_file_name: {json_file_name}")
with open(json_file_name, "w") as outfile:
    outfile.write(json_object)
print(f"{json_file_name} isExist: {os.path.exists(json_file_name)}")

date_time = workflow_infos['date_time']
print(f"date_time: {date_time}")

# 上傳 JSON 到 Blob
blob_datastore.upload_files([
  json_file_name
], target_path=date_time, overwrite=True)

# 發送 Microsoft Teams 通知
teams_notify.attachments_content_body(workflow_infos)

# 傳送通知到 Edge
registry_manager = IoTHubRegistryManager(iot_hub_connection_string_secret)

msg = {
    "file_url": datas['file_url'],
    "json_url": datas['json_url']
}

# 設定 IoT Hub Device ID
iot_hub_device_id = keyvault.get_secret(name="iot-hub-device-id")
print(f"iot_hub_device_id: {iot_hub_device_id}")

registry_manager.send_c2d_message(
    iot_hub_device_id,
    json.dumps(msg),
    properties={}
)
