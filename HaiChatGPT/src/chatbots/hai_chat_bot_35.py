"""
HaiChatBot via OpenAI API_KEY, based on GPT-3
"""

import os
import copy
import traceback

from ...repos.ChatGPT.src.revChatGPT.V3 import Chatbot

import damei as dm
import time

logger = dm.get_logger('hai_chat_bot_35')

class HChatBot(Chatbot):

    def __init__(self, 
                api_key: str,
                engine: str = None,
                proxy: str = None,
                max_tokens: int = 3000,
                temperature: float = 0.5,
                top_p: float = 1.0,
                reply_count: int = 1,
                system_prompt: str = "You are ChatGPT, a large language model trained by OpenAI. Respond conversationally",
                **kwargs,
                ) -> None:
        api_key = api_key or os.getenv("OPENAI_API_KEY")

        super().__init__(api_key, engine, proxy, max_tokens, temperature, top_p, reply_count, system_prompt)
        self.temperature = temperature

        # 为对话增加的设置
        self.max_qa = kwargs.pop('max_qa', 5)
        self.qa_pairs = []  # 保存历史的问答对qustion, answer
        self.show_history = False

        self.show_last_question = False
        self.show_last_answer = False
        self.last_question = None
        self.last_answer = None

        self.error_handler = ErrorHandler()

    def append_qa(self, text, answer):
        if len(self.qa_pairs) >= self.max_qa:
            self.qa_pairs.pop(0)
        self.qa_pairs.append((text, answer))

    def set_api_key(self, api_key: str) -> None:
        self.api_key = api_key

    def set_engine(self, engine: str) -> None:
        self.engine = engine

    def set_temperature(self, temperature: float) -> None:
        self.temperature = temperature

    def _query_stream(self, query):

        ret = self.ask_stream(
            prompt=query,
            role="user",
            convo_id='default',
            )
        
        self.last_answer = ''
        
        def convert_generator():
            text = ''
            for content in ret:
                text += content
                b = text.replace("\n", "<|im_br|>")
                yield f'data: {b}\n\n'
                # time.sleep(0.01)
            self.last_answer = text
        return convert_generator()
        
        
    def query_stream(self, query):
        """包含错误处理的query_stream"""
        try:
            generator = self._query_stream(query)
            return generator
        except Exception as e:
            error_info = self.error_handler.handle(e)
            return error_info


class ErrorHandler:
    
    """
    error类型：
    openai.error.RateLimitError， 点击速率太快

    """

    def text2generator(self, text):
        """
        text: string
        text转为generator
        """
        def generator():
            for line in text:
                yield f'data: {line}\n\n'
                time.sleep(0.01)
        return generator()
         

    def handle(self, e):
        
        error_info = f'{type(e)}: {e}'
        logger.error(f'{error_info}\n {traceback.format_exc()}')
        return self.text2generator(error_info)

    


    
        
        





