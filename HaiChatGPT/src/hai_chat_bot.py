import os
import copy
import traceback

from ..repos.ChatGPT.src.revChatGPT.Official import Chatbot, AsyncChatbot

import damei as dm
import time

ENGINE = "text-davinci-003"
# ENGINE = "text-chat-davinci-002-20221215"

logger = dm.get_logger('hai_chat_bot')


class HChatBot(Chatbot):

    def __init__(self, 
                api_key: str = None, 
                buffer: int = None, 
                engine: str = None, 
                proxy: str = None,
                temperature: float = 0.5,
                ) -> None:
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        engine = ENGINE

        super().__init__(api_key, buffer, engine, proxy)
        self.temperature = temperature

        # 为对话增加的设置
        self.max_qa = 5
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

    def query(self, query) -> str:
        """
        :param query: 请求的文字，纯文本
        """
        temp = self.temperature
        cvid = None  # conversation id
        user = 'User'

        
        if cvid is not None:
            # 加载旧会话，主要功能是将旧的会话内容加入到prompt的chat_history属性中
            self.load_conversation(cvid)

        # 构建prompt, 包括base, chat_history, query，自动控制缓存大小
        prompt = self.prompt.construct_prompt(
                    new_prompt=query,
                    custom_history=None,
                    user=user,
                    )

        # 调用openai api，获取completion
        completion = self._get_completion(
                    prompt=prompt,
                    temperature=temp,
                    )
        
        # 后处理，如Choices报错，有时选取最优回答。将query和completion加入到chat_history中，如果指定cvid, 将历史同时保存到会话历史中
        completion = self._process_completion(
                    user_request=query,
                    completion=completion,
                    conversation_id=None,
                    user=user,
                    )

        response = completion['choices'][0]['text']  # 选取最优回答

        return response


    def _query_stream(self, query):
        """
        return a generator
        无错误处理，新增query_stream里面的错误处理
        """
        temp = self.temperature
        cvid = None  # conversation id
        user = 'User'

        
        if cvid is not None:
            self.load_conversation(cvid)

        prompt = self.prompt.construct_prompt(
                    new_prompt=query,
                    custom_history=None,
                    user=user,
                    )
        
        completion = self._get_completion(
                    prompt=prompt,
                    temperature=temp,
                    stream=True,
                    )

        generator = self._process_completion_stream(
                    user_request=query,
                    completion=completion,
                    conversation_id=cvid,
                    user=user,
                    )

        # self.last_question = query
        self.last_answer = ''
        def convert_generator():
            # str_need_del = "<|im_end|>"
            str_need_del_list = ["<|im", "_", "end", "|", ">", ""]
            idx = 0
            next_skip = None
            continuous = False
            for x in generator:
                if x in [" <|im", "<|im", "><|im"]:
                    # idx = str_need_del_list.index(x)
                    next_skip = str_need_del_list[idx + 1]
                    print(f'make next_skip: {next_skip}')
                    continuous = True
                    continue
                elif x == next_skip and continuous:  # x: _ 
                    idx += 1
                    try:
                        next_skip = str_need_del_list[idx + 1]
                    except:
                        next_skip = None
                    continue
                continuous = False
                # print(f'data: {x} next_skip: {next_skip}')
                yield f'data: {x}\n\n'
                self.last_answer += x
        converted_generator = convert_generator()
        # self.new_question = query
        return converted_generator

    
    def query_stream(self, query):
        """包含错误处理"""
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

    


    
        
        





