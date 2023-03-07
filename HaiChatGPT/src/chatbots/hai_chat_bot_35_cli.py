


from ...repos.ChatGPT.src.revChatGPT.V3 import Chatbot


class HChatBot(Chatbot):

    def __init__(
        self,
        api_key: str,
        engine: str = None,
        proxy: str = None,
        max_tokens: int = 3000,
        temperature: float = 0.5,
        top_p: float = 1.0,
        reply_count: int = 1,
        system_prompt: str = "You are ChatGPT, a large language model trained by OpenAI. Respond conversationally",
    ) -> None:
        super().__init__(
            api_key,
            engine,
            proxy,
            max_tokens,
            temperature,
            top_p,
            reply_count,
            system_prompt,
        )

    
        

