import os
import json 
from azureml.core import Run
from azure.iot.hub import IoTHubRegistryManager
import teams_notify
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--evaluate_input", dest="evaluate_input", required=True)
args = parser.parse_args()
print(f"Argument evaluate_input: {args.evaluate_input}")

# 取得 Workspace
run = Run.get_context()
ws = run.experiment.workspace

# 取得 Blob Key
keyvault = ws.get_default_keyvault()

# 取得 IoT Hub Connection String
iot_hub_connection_string_secret = keyvault.get_secret(name="iot-hub-connection-string")

# 取得 Evaluate 傳來的資料
print(f"evaluate_input: {os.listdir(args.evaluate_input)}")

jsonIsExisting = os.path.exists(f"{args.evaluate_input}/workflow_infos.json")
print(f"workflow_infos.json is exist: {jsonIsExisting}")

json_file = open(f"{args.evaluate_input}/workflow_infos.json")
datas = json.load(json_file)
json_file.close()
print(f"json_context: {datas}")

# 發送 Microsoft Teams 通知
teams_notify.attachments_content_body(datas["workflow_infos"])

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