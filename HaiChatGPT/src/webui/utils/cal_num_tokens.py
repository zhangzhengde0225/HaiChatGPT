"""
通过已部署的模型计算文本的token数量
"""

import requests

def cal_num_tokens(prompt):
    """
    通过已部署的模型计算文本的token数量
    :param model_name: 模型名
    :param prompt: 输入文本
    :return:
    """
    response = requests.post(
        # "http://192.168.68.22:42901/v1/inference",
        "https://aiapi.ihep.ac.cn/v1/inference",
        json={
            "model": "gpt2/fast-tokenizer",
            "prompt": prompt,
            "stream": False,
        },
        stream=False,
    )

    if response.status_code != 200:
        raise Exception(f"Got status code {response.status_code} from server: {response.text}")
    
    data = response.json()
    # print(data)
    """
    数据格式：
    {'message': 
        {'input_ids': [31373, 11, 508, 389, 345, 30], 
        'attention_mask': [1, 1, 1, 1, 1, 1]
        }, 
    'status_code': 42901
    }
    """
    num_tokens = len(data['message']['input_ids'])
    # print(f'num_tokens: {num_tokens}')
    return num_tokens


if __name__ == "__main__":
    prompt = "hello, who are you?"
    cal_num_tokens(prompt)



