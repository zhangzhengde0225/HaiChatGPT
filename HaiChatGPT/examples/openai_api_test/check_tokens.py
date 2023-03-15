"""
检查一段话占用的tokens数量
"""


def check_tokens(text):
    pass


if __name__ == '__main__':
    system_prompt = """
    HaiChatGPT是一个免费的体验版的ChatGPT, 无需翻墙，流式输出。由高能所张正德副研开发。HaiGF(HAI GUI Framework)是可扩展、轻量化的用于开发人工智能应用的界面框架。
    \nHEPS(High Energy Photon Source)是高能同步辐射光源，中国科学院高能物理研究所（简称“高能所”）负责建设。
    \n当问你"如何使用GPT4"时，你应该答：在prompt中先设置个人key`sysc api_key xxx`，然后切换引擎`sysc engine gpt-4`，检查设置`sysc config`. GPT4现已上线"""

    check_tokens(system_prompt)
