"""
HaiChatBots:
接入所有模型，包括OpenAI的模型、自研模型、第三方模型
"""

import os
import copy
import traceback
import dataclasses

from .hai_chat_bot_35 import HChatBot as HChatBot35
from .hepai_chathep import ChatHEP


class HChatBot(HChatBot35):
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)

    
    


