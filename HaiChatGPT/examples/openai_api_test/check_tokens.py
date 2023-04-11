"""
检查一段话占用的tokens数量
"""
import time

def check_tokens(text):
    """看起来慢，实际所加载tokenizer时慢"""
    from transformers import GPT2TokenizerFast
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

    print('tokenize...')
    for i in range(10):
        t0 = time.time()
        ret = tokenizer(text)
        # ret2 = tokenizer(" Hello world")['input_ids']
        print(f'time: {(time.time() - t0)*1000:.5f}ms')
    num_tokens = len(ret['input_ids'])
    num_chars = len(text)
    print(ret)
    print(f'num_tokens: {num_tokens}, num_chars: {num_chars}')
    pass


if __name__ == '__main__':
    system_prompt = """
    HaiChatGPT是一个免费的体验版的ChatGPT, 无需翻墙，流式输出。由高能所张正德副研开发。HaiGF(HAI GUI Framework)是可扩展、轻量化的用于开发人工智能应用的界面框架。
    \nHEPS(High Energy Photon Source)是高能同步辐射光源，中国科学院高能物理研究所（简称“高能所”）负责建设。
    \n当问你"如何使用GPT4"时，你应该答：在prompt中先设置个人key`sysc api_key xxx`，然后切换引擎`sysc engine gpt-4`，检查设置`sysc config`. GPT4现已上线"""

#     system_prompt = """
#     Many words map to one token, but some don't: indivisible.

# Unicode characters like emojis may be split into many tokens containing the underlying bytes: 🤚🏾

# Sequences of characters commonly found next to each other may be grouped together: 1234567890"""
    check_tokens(system_prompt)
