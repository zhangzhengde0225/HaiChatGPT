import os


from ..repos.ChatGPT.src.revChatGPT.Official import Chatbot, AsyncChatbot


ENGINE = "text-davinci-003"

class HChatBot(Chatbot):

    def __init__(self, 
                api_key: str, 
                buffer: int = None, 
                engine: str = None, 
                proxy: str = None) -> None:
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        engine = ENGINE

        super().__init__(api_key, buffer, engine, proxy)



