import os


from ..repos.ChatGPT.src.revChatGPT.Official import Chatbot, AsyncChatbot


ENGINE = "text-davinci-003"

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

        pass

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


    def query_stream(self, query):
        """
        return a generator
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

        return generator

        
        





