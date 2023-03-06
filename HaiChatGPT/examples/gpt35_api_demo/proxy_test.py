api_key = "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"
# api_key = "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"

import requests

proxy = "http://localhost:1086"
# proxy = "localhost:1086"
proxies = {
    "http": proxy,
    "https": proxy,
}

url = "https://api.openai.com/v1/models"
url = "https://api.openai.com/v1/chat/completions"
session = requests.Session()
session.proxies = proxies

response = session.post(
    url, 
    proxies=session.proxies,
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": "gpt-3.5-turbo-0301",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "用python写冒泡排序"},
            ],
        
        }
    )

if response.status_code == 200:
    print('OK')
    print(response.json())
else:
    print(response.status_code)
    print(response.text)