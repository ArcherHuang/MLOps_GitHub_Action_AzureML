import os
import json
import time
from azure.iot.device import IoTHubDeviceClient
import wget
from dotenv import load_dotenv
load_dotenv()

iot_hub_device_connection_string = os.getenv("IOT_HUB_DEVICE_CONNECTION_STRING")

def message_handler(message):
    json_str = message.data.decode('utf-8')
    print(f"json_str: {json_str}, type: {type(json_str)}\n")

    file_url = json.loads(json_str)['file_url']
    json_url = json.loads(json_str)['json_url']
    file_name = file_url.rsplit('/', 1)[-1]
    json_name = json_url.rsplit('/', 1)[-1]

    model_path = '../Models'
    isExist = os.path.exists(model_path)
    if not isExist:
        os.makedirs(model_path)

    wget.download(file_url, f"../Models/{file_name}")
    wget.download(json_url, f"../Models/{json_name}")

def main():
    print ("Starting the Python IoT Hub C2D Messaging device sample...")
    client = IoTHubDeviceClient.create_from_connection_string(iot_hub_device_connection_string)

    print ("Waiting for C2D messages, press Ctrl-C to exit")
    try:
        client.on_message_received = message_handler

        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        print("IoT Hub C2D Messaging device sample stopped")
    finally:
        print("Shutting down IoT Hub Client")
        client.shutdown()

if __name__ == '__main__':
    main()