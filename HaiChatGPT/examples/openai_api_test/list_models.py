
import requests
import damei as dm

session = requests.Session()


def list_models(api_key, proxy=None, model_name=None):
    proxies = proxy if proxy is None else {
        "http": proxy,
        "https": proxy,
        }

    url = "https://api.openai.com/v1/models"
    url = url if model_name is None else f"https://api.openai.com/v1/models/{model_name}"
    headers = {
        "Authorization": f"Bearer {api_key}"}
    
    response = session.get(
        url,
        headers=headers,
        proxies=proxies,
    )
    response.raise_for_status()
    
    # 输出
    json = response.json()
    """
    格式：
    {
        "data": [
            {
            "id": "model-id-0",
            "object": "model",
            "owned_by": "organization-owner",
            "permission": [...]
            },
            {
            "id": "model-id-1",
            "object": "model",
            "owned_by": "organization-owner",
            "permission": [...]
            },
            {
            "id": "model-id-2",
            "object": "model",
            "owned_by": "openai",
            "permission": [...]
            },
        ],
        "object": "list"
    }
    """
    # print(f'json: {json}')
    data = json['data'] if model_name is None else [json]
    for i, model in enumerate(data):
        model_name = model['id']
        print(f'{i+1:>2}th model: {model_name}')
        # info = dm.misc.dict2info(model)
        # print(info)
    print()
    # 查看所有gpt模型
    gpt_models = [model for model in data if 'gpt'in model['id']]
    for i, model in enumerate(gpt_models):
        info = dm.misc.dict2info(model)
        print(f'{i+1}th gpt model: \n{info}')


if __name__ == '__main__':
    from utils import get_api_key
    api_key = get_api_key()
    print(api_key)
    proxy = 'http://127.0.0.1:1086'
    model_name = None
    model_name = 'gpt-3.5-turbo'
    
    list_models(api_key, proxy, model_name)



