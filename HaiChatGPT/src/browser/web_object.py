
import os, sys
import time
import damei as dm
from flask import Flask, redirect, render_template, request, url_for
from flask import Response
import requests
from .app import app
from HaiChatGPT.apis import HChatBot

logger = dm.get_logger('web_object')


class FakeChatGPT(object):
    def __init__(self) -> None:
       
        self.count = 0
        self.max_qa = 50
        self.qa_pairs = []  # 保存历史的问答对qustion, answer

        # self.query('question1')
        # self.query('question2')
        self.has_new_pair = False
    
    def append_qa(self, text, answer):
        if len(self.qa_pairs) >= self.max_qa:
            self.qa_pairs.pop(0)
        self.qa_pairs.append((text, answer))
        
    def query(self, text):
        answer = f'I am the answer {self.count} for "{text}".'
        self.count += 1
        return answer

    def query_stream(self, text):
        def generator():
            data = f'I am the stream answer {self.count} for "{text}"'
            for x in data:
                yield f'data: {x}\n\n'
                time.sleep(0.1)
        generator = generator()
        # # self.append_qa(text, answer)
        # self.count += 1
        return generator

class WebObject(object):
    """
    与web对象交互，强绑定
    """

    def __init__(self) -> None:
        self._stream = True
        """
        为适应不同ip的请求，不同的ip需要不同的chatbot
        """
        self.chatbots = {}  # key: ip, value: chatbot
        self.qa_pairs = []
        self.qa_pairs.append(('你是谁？', '我是 ChatGPT，一个由 OpenAI 训练的大型语言模型。有什么可以帮助你的？'))

    def has_new_pair(self, ip):
        if ip not in self.chatbots:
            # raise ValueError(f'ip: {ip} not in chatbots')
            return False
        else:
            chatbot = self.chatbots[ip]
            return chatbot.has_new_pair
    
    def get_qa_pairs(self, ip):
        if ip not in self.chatbots:
            # raise ValueError(f'ip: {ip} not in chatbots')
            return []
        else:
            chatbot = self.chatbots[ip]
            return chatbot.qa_pairs

    def get_generator(self, ip, text):
        if ip not in self.chatbots:
            # raise ValueError(f'ip: {ip} not in chatbots')
            return []
        else:
            chatbot = self.chatbots[ip]
            generator = chatbot.query_stream(text)
            return generator

    def pop_qa_pairs(self, ip):
        """其实并没有清空，知识将has_new_pair设置为False"""
        if ip not in self.chatbots:
            return []
        else:
            chatbot = self.chatbots[ip]
            qa_pairs = chatbot.qa_pairs
            chatbot.has_new_pair = False
            return qa_pairs

    def create_new_chatbot(self):
        # chatbot = HChatBot()
        chatbot = FakeChatGPT()
        return chatbot

    def query(self, ip, text):
        """
        text: request txt.
        """
        if ip not in self.chatbots:
            chatbot = self.create_new_chatbot()
            self.chatbots[ip] = chatbot
        else:
            chatbot = self.chatbots[ip]

        if not self._stream:
            answer = chatbot.query(text)
            chatbot.append_qa(text, answer)
            chatbot.has_new_pair = True
            return redirect(url_for("index", result=answer))
        else:
            generator = chatbot.query_stream(text)
            answer = 'stream answer'
            chatbot.append_qa(text, answer)
            chatbot.has_new_pair = True
            return redirect(url_for("index", result=''))
            # sys.stdout.flush()
            # full_answer = ''
            # for data in generator:
            #     # logger.info(f'result: {ret}')
            #     print(data)
            #     sys.stdout.flush()
            #     # yield self.render(data)
            #     full_answer += data
            # chatbot.append_qa(text, full_answer)
            # print('webo generator end.')
            # # return Response(generator(), mimetype="text/event-stream")
            # return redirect(url_for("index", result=full_answer))

    def render(self, ret, **kwargs):
        return redirect(url_for("index", result=ret))

    


class ErrorHandler:
    
    """
    error类型：
    openai.error.RateLimitError， 点击速率太快
    """

