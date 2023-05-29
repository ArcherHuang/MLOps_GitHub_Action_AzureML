import argparse
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import pandas as pd
import cv2
from azureml.core import Run
from azureml.pipeline.core import PipelineData
from azureml.core import Datastore
from azureml.core import Workspace #, PublishedPipeline
from datetime import datetime
from azureml.core import Dataset
from azureml.core import Model
import json 
import shutil
import matplotlib.pyplot as plt

# 設定 Model 名稱 
model_name="tf-iris-decision-tree"

parser = argparse.ArgumentParser()
parser.add_argument("--blob_container_name", type=str, help="output path")
parser.add_argument("--blob_account_name", type=str, help="output path")
parser.add_argument("--training_datasets", type=str, help="output path")
parser.add_argument("--test_datasets", type=str, help="output path")
parser.add_argument("--output_folder", type=str, required=True)

args = parser.parse_args()
print(f"Argument blob_container_name: {args.blob_container_name}")
print(f"Argument blob_account_name: {args.blob_account_name}")
print(f"Argument training_datasets: {args.training_datasets}")
print(f"Argument test_datasets: {args.test_datasets}")
print(f"Argument output_folder: {args.output_folder}")

print(f"training_datasets: {os.listdir(args.training_datasets)}")
print(f"test_datasets: {os.listdir(args.test_datasets)}")

# 取得 Workspace
run = Run.get_context()
ws = run.experiment.workspace

# 取得 Blob Key
keyvault = ws.get_default_keyvault()
# print(f"list secret: {keyvault.list_secrets()}")
retrieved_secret = keyvault.get_secret(name="blob-account-key")

# 設定 Datastore
blob_datastore = Datastore.register_azure_blob_container(workspace=ws, 
                                                         datastore_name=args.blob_container_name, 
                                                         container_name=args.blob_container_name, 
                                                         account_name=args.blob_account_name,
                                                         account_key=retrieved_secret)

# 設定隨機種子，以確保每次執行結果相同
np.random.seed(0)

# 讀取 CSV 檔案
training_file = f"{args.training_datasets}/iris_training.csv"
test_file = f"{args.test_datasets}/iris_test.csv"

training_data = pd.read_csv(training_file, header=0)
test_data = pd.read_csv(test_file, header=0)

# 擷取特徵和標籤
training_features = training_data.iloc[:, :-1].values
training_labels = training_data.iloc[:, -1].values
test_features = test_data.iloc[:, :-1].values
test_labels = test_data.iloc[:, -1].values

# 將標籤轉換為 one-hot 編碼
training_labels = tf.keras.utils.to_categorical(training_labels, num_classes=3)
test_labels = tf.keras.utils.to_categorical(test_labels, num_classes=3)

# 定義模型
model = tf.keras.models.Sequential([
  tf.keras.layers.Dense(10, input_shape=(4,), activation=tf.nn.relu),
  tf.keras.layers.Dense(10, activation=tf.nn.relu),
  tf.keras.layers.Dense(3, activation=tf.nn.softmax)
])

# 編譯模型
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
              
# 訓練模型
epoch_count = 50
history_callback = model.fit(training_features, training_labels, epochs=epoch_count, batch_size=10)
metrics = history_callback.history
print(f"metrics: {metrics}")
run.log_list("train_loss", metrics["loss"][:10])
run.log_list("epoch", [epoch_count])

# 評估模型
loss, accuracy = model.evaluate(test_features, test_labels)
print(f"[Training Step] accuracy: {accuracy}")
run.log("[Training Step] accuracy", accuracy)

# 儲存模型 ( 只能將模型存在 outputs 這個資料夾之下，後續才能註冊模型到 Models 中 )
model.save("iris_model")
run.upload_folder(name="outputs/iris_model", path="iris_model")
print("Saved Model")

# 將 Models 相關檔案上傳到 Azure Blob
# for dirpath, dirnames, filenames in os.walk("iris_model"):
#   for filename in filenames:
#     print(f"dirpath: {dirpath}, filename: {filename}") 
#     blob_datastore.upload_files([
#       os.path.join(dirpath, filename)
#     ], target_path=f"{date_time}/{dirpath}", overwrite=True)

# 取得 Secret Info
keyvault = ws.get_default_keyvault()
commit_sha = keyvault.get_secret(name="commit-sha")
github_repository = keyvault.get_secret(name="github-repository")
commit_url = keyvault.get_secret(name="commit-url")
committer = keyvault.get_secret(name="committer")
commit_timestamp = keyvault.get_secret(name="commit-timestamp")
commit_message = keyvault.get_secret(name="commit-message")
github_workflow = keyvault.get_secret(name="github-workflow")
github_action_run_id = keyvault.get_secret(name="github-action-run-id")
github_action_run_number = keyvault.get_secret(name="github-action-run-number")

print(f"commit_sha: {commit_sha}")
print(f"github_repository: {github_repository}")
print(f"commit_url: {commit_url}")
print(f"committer: {committer}")
print(f"commit_timestamp: {commit_timestamp}")
print(f"commit_message: {commit_message}")
print(f"github_workflow: {github_workflow}")
print(f"github_action_run_id: {github_action_run_id}")
print(f"github_action_run_number: {github_action_run_number}")

commit_timestamp_replace = commit_timestamp.replace("-", "").replace("T", "_").replace(":", "").replace("+0800", "")
print(f"commit_timestamp: {commit_timestamp}, commit_timestamp_replace: {commit_timestamp_replace}")

# 將 Models 相關檔案以 commit_sha.zip 壓縮後上傳到 Azure Blob
shutil.make_archive(commit_sha, 'zip', 'iris_model')
blob_datastore.upload_files([
  f"{commit_sha}.zip"
], target_path=commit_timestamp_replace, overwrite=True)

# Create Loss Chart and Upload
plt.plot(metrics["loss"][:10])
plt.xlabel('Epoch')
plt.ylabel('Training Loss')
plt.savefig('train_loss.jpg')
blob_datastore.upload_files([
  "train_loss.jpg"
], target_path=commit_timestamp_replace, overwrite=True)

# 取得 AzureML Data assets Version
fileIrisTrainData = Dataset.get_by_name(ws, 'IrisTrainFileData')
fileIrisTestData = Dataset.get_by_name(ws, 'IrisTestFileData')

print(f"fileIrisTrainData version: {fileIrisTrainData.version}")
print(f"fileIrisTestData version: {fileIrisTestData.version}")

# 註冊 Model 相關檔案到 AzureML
run.register_model( 
  model_name=model_name,
  model_path="outputs/iris_model",
  model_framework="keras",
  model_framework_version="2.2.4",
  description="A decision tree model for the iris dataset",
  tags={
    "Training context": "Pipeline"
  },
  properties={
    "train_loss": metrics["loss"][:10],
    "epoch": 50,
    "commit_sha": commit_sha,
    "fileIrisTrainData": fileIrisTrainData.version,
    "fileIrisTestData": fileIrisTestData.version,
    "commit_url": commit_url,
    "committer": committer,
    "commit_timestamp": commit_timestamp,
    "commit_message": commit_message,
    "github_workflow": github_workflow,
    "github_action_run_id": github_action_run_id,
    "github_action_run_number": github_action_run_number
  }
)

# 取得 AzureML Model Version
print(f"Model Latest Version: {Model.list(ws)[0].version}")

# 存放 Workflow 相關資訊
workfow_info = {
  "date_time": commit_timestamp_replace,
  "data_assets_version": {
    "fileIrisTrainData": fileIrisTrainData.version,
    "fileIrisTestData": fileIrisTestData.version
  },
  "commit_info": {
    "github_repository": github_repository,
    "commit_url": commit_url,
    "committer": committer,
    "commit_timestamp": commit_timestamp,
    "commit_message": commit_message,
    "github_workflow": github_workflow,
    "commit_sha": commit_sha,
    "github_action_run_id": github_action_run_id,
    "github_action_run_number": github_action_run_number
  },
  "train_info": {
    "train_loss": metrics["loss"][:10],
    "epoch": epoch_count,
    "accuracy": accuracy
  },
  "model_version": Model.list(ws)[0].version,
  "images": {
    "train_loss_name": "train_loss.jpg"
  }
}

# Pipeline 間訊息交換
parameter_json = {
  "model_name": model_name,
  "file_url": f"https://irissamples.blob.core.windows.net/models/{commit_timestamp_replace}/{commit_sha}.zip",
  "json_url": f"https://irissamples.blob.core.windows.net/models/{commit_timestamp_replace}/{commit_sha}.json",
  "workfow_info": workfow_info
}

with open(os.path.join(args.output_folder, "OutputFileDatasetConfig-Parameter.json"), "w") as outfile:
  json.dump(parameter_json, outfile)
