"""
HaiChatBot via Access Token (based on GPT-3.5)
"""

from ...repos.ChatGPT_token.src.revChatGPT.V1 import Chatbot, AsyncChatbot

from .hai_chat_bot import ErrorHandler


class HTokenChatBot(Chatbot):

    def __init__(
        self, 
        config: dict[str, str], 
        conversation_id: str = None, 
        parent_id: str = None, 
        session_client=None, 
        lazy_loading: bool = False,
        **kwargs
        ) -> None:
        super().__init__(config, conversation_id, parent_id, session_client, lazy_loading)

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
    
    def _query_stream(self, query):
        """包含错误处理的query_stream"""
        generator = self.ask(prompt=query)

        self.last_answer = ''
        
        def convert_generator():
            prev_text = ''
            for data in generator:
                text = data["message"][len(prev_text)::]
                yield f'data: {text}\n\n'
                prev_text = data["message"]
            self.last_answer = data["message"]
        return convert_generator()
        
    def query_stream(self, query):
        """包含错误处理的query_stream"""
        try:
            generator = self._query_stream(query)
            return generator
        except Exception as e:
            error_info = self.error_handler.handle(e)
            return error_info
        
    




