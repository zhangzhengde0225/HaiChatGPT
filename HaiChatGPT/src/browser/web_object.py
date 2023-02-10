
import os, sys
import damei as dm
from flask import Flask, redirect, render_template, request, url_for

logger = dm.get_logger('web_object')

class FakeChatGPT(object):
    def __init__(self) -> None:
        self.count = 0

    def query(self, text):
        self.count += 1
        return f'I am the anser {self.count}.'

class WebObject(object):
    """
    与web对象交互，强绑定
    """

    def __init__(self) -> None:
        self.stream = True
        self._init_chatbot()

    def _init_chatbot(self):
        try:
            from HaiChatGPT.apis import HChatBot
            self.chatbot = HChatBot()
        except Exception as e:
            logger.error(f'Failed to import HChatBot: {e}\nUse FakeChatGPT instead.')
            self.chatbot = FakeChatGPT()

    def query(self, text):
        """
        text: request txt.
        """
        if not self.stream:
            ret = self.chatbot.query(text)
            # logger.debug(f'result: {ret}')
            logger.info(f'result: {ret}')
            return self.render(ret)
        else:
            generator = self.chatbot.query_stream(text)
            print('webo generator: ', generator)
            sys.stdout.flush()
            for ret in generator:
                # logger.info(f'result: {ret}')
                print(ret)
                sys.stdout.flush()
                yield self.render(ret)
            print('webo generator end.')

    def render(self, ret, **kwargs):
        return redirect(url_for("index", result=ret))


class ErrorHandler:
    
    """
    error类型：
    openai.error.RateLimitError， 点击速率太快
    """

