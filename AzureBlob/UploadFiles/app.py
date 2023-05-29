import os
from dotenv import load_dotenv
from azure.storage.blob import BlobClient
from datetime import datetime, timezone, timedelta

date_time = datetime.now(timezone(timedelta(hours=+8))).strftime("%Y%m%d_%H%M%S")

load_dotenv()
BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")

for dirpath, dirnames, filenames in os.walk("../../Datasets"):
  for filename in filenames:
    if not filename == '.DS_Store':
        parent_path = dirpath.replace('../../Datasets/', '')
        print(f"dirpath: {parent_path}, filename: {filename}")
        try:
            blob = BlobClient.from_connection_string(
                conn_str = BLOB_CONNECTION_STRING,
                container_name = BLOB_CONTAINER_NAME,
                blob_name = f"{parent_path}/{date_time}/{filename}"
            )
            with open(f"{dirpath}/{filename}", "rb") as data:
                blob.upload_blob(data, overwrite=True)
        except Exception as ex:
            print(f"Exception: {ex}")