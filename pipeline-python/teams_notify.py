from azureml.core import Run
import requests

# 取得 Workspace
run = Run.get_context()
ws = run.experiment.workspace

# 取得 Commit ID & Blob base url
keyvault = ws.get_default_keyvault()
teams_webhook = keyvault.get_secret(name="teams-webhook")
blob_model_base_url = keyvault.get_secret(name="blob-model-base-url")
print(f"teams_webhook: {teams_webhook}")
print(f"blob_model_base_url: {blob_model_base_url}")

# 設定 API Header 類型
headers = {
    "Content-Type": "application/json"
}

# 組 text 字串
def message_format(data, type=""):
    text = ""
    print(f"type: {type}")
    if type == "commit_info":
        commit_time = data['commit_timestamp'].replace("T", " ").replace("+08:00", "")
        text = f"- Repository: {data['github_repository']} [【 Open Repo 】](https://github.com/{data['github_repository']})\r- Committer: {data['committer']} \r- Timestamp: {commit_time}\r- SHA: {data['commit_sha']} [【 Open Commit URL 】]({data['commit_url']})\r- Commit Message: {data['commit_message']}\r- Workflow: {data['github_workflow']} ([#{data['github_action_run_number']}](https://github.com/{data['github_repository']}/actions/runs/{data['github_action_run_id']}))\r"
    else:
        for key in data.keys():
            print(f"key: {key}, value: {data[key]}")
            if key != 'train_loss':
                text = f"{text}- {key}: {data[key]} \r"
    print(f"text: {text}")
    return text

# 組 body 訊息串列
def attachments_content_body(json_object):
    content_body = []
    content_body.append({
        "type": "TextBlock",
        "text": "**GitHub Commit Info**"
    })
    print(f"json_object: {json_object}")
    print(f"commit_info: {json_object['commit_info']}")
    text = message_format(json_object['commit_info'], "commit_info")
    content_body.append({
        "type": "TextBlock",
        "text": f"{text}",
        "wrap": True
    })
    content_body.append({
        "type": "TextBlock",
        "text": "**AzureML Data Assets Version**"
    })
    text = message_format(json_object['data_assets_version'])
    content_body.append({
        "type": "TextBlock",
        "text": f"{text}",
        "wrap": True
    })
    content_body.append({
        "type": "TextBlock",
        "text": "**AzureML Model Version**"
    })
    content_body.append({
        "type": "TextBlock",
        "text": f"- Version: {json_object['model_version']} [【 Download 】]({blob_model_base_url}/{json_object['date_time']}/{json_object['commit_info']['commit_sha']}.zip)\r",
        "wrap": True
    })
    content_body.append({
        "type": "TextBlock",
        "text": "**AzureML Train Info**"
    })
    text = message_format(json_object['train_info'])
    print(f"train_info: {text}")
    content_body.append({
        "type": "TextBlock",
        "text": f"{text}",
        "wrap": True
    })
    content_body.append({
        "type": "TextBlock",
        "text": "**AzureML Evaluate Info**"
    })
    text = message_format(json_object['evaluate_info'])
    content_body.append({
        "type": "TextBlock",
        "text": f"{text}",
        "wrap": True
    })
    content_body.append({
        "type": "TextBlock",
        "text": "**Train Loss**"
    })
    content_body.append({
        "type": "TextBlock",
        "text": f"- [【 Download Image 】]({blob_model_base_url}/{json_object['date_time']}/{json_object['images']['train_loss_name']})\r",
        "wrap": True
    })
    content_body.append({  
        "type": "Image",  
        "url": f"{blob_model_base_url}/{json_object['date_time']}/{json_object['images']['train_loss_name']}"      
    })
    print(f"content_body: {content_body}")
    notify(content_body)

# 傳送 Teams Notify
def notify(content_body):
    try:
        data = {
            "type": "message",
            "attachments":[
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": "",
                    "content":{
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": content_body
                    }
                }
            ]
        }

        response = requests.post(teams_webhook, headers=headers, json=data)
        print(response)
        return response.status_code
    except Exception as err:
        print('Other error occurred %s' % {err})
