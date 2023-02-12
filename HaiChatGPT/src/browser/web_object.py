
import os, sys
import time
import damei as dm
from flask import Flask, redirect, render_template, request, url_for
from flask import Response
import requests
from .app import app
try:
    from HaiChatGPT.apis import HChatBot
except:
    from ..hai_chat_bot import HChatBot
from .fake_bot import FakeChatGPT

# logger = dm.get_logger('web_object')
import logging
from pathlib import Path


logg_dir = f'{Path.home()}/.logs/haichatgpt/{Path(os.getcwd()).name}'
if not os.path.exists(logg_dir):
    os.makedirs(logg_dir)
save_path = f'{logg_dir}/{Path(os.getcwd()).name}.log'
handler = logging.FileHandler(save_path)
# handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

def getLogger(name=None, **kwargs):

    name = name if name else 'root'
    name_lenth = kwargs.get('name_lenth', 12)
    name = f'{name:<{name_lenth}}'
    logger = logging.getLogger(name)
    # level = kwargs.get('level', LOGGING_LEVEL)
    level = kwargs.get('level', logging.DEBUG)
    format_str = f"\033[1;35m[%(asctime)s]\033[0m \033[1;32m[%(name)s]\033[0m " \
                 f"\033[1;36m[%(levelname)s]:\033[0m %(message)s"
    logging.basicConfig(level=level,
                        format=format_str,
                        # datefmt='%d %b %Y %H:%M:%S'
                        )
    logg_dir = f'{Path.home()}/.logs/haichatgpt/{Path(os.getcwd()).name}'
    if not os.path.exists(logg_dir):
        os.makedirs(logg_dir)
    fh = logging.FileHandler(f'{logg_dir}/{Path(os.getcwd()).name}.log')
    fh.setLevel(level=level)
    # ch = logging.StreamHandler()
    # ch.setLevel(level=level)
    fh.setFormatter(logging.Formatter(format_str))
    # ch.setFormatter(logging.Formatter(format_str))
    logger.addHandler(fh)
    # logger.addHandler(ch)
    return logger

logger = getLogger('web_object')

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
        self.query_count = 0
    
    def get_bot_by_ip(self, ip, create_new=True):
        if ip not in self.chatbots:
            if create_new:
                chatbot = self.create_new_chatbot()
                self.chatbots[ip] = chatbot
                return chatbot
            else:
                return None
        else:
            chatbot = self.chatbots[ip]
            return chatbot

    def delete_bot_by_ip(self, ip):
        if ip in self.chatbots:
            del self.chatbots[ip]

    def has_new_pair(self, ip):
        if ip not in self.chatbots:
            # raise ValueError(f'ip: {ip} not in chatbots')
            return False
        else:
            chatbot = self.chatbots[ip]
            return chatbot.has_new_pair
    
    # def get_qa_pairs(self, ip):
    #     if ip not in self.chatbots:
    #         # raise ValueError(f'ip: {ip} not in chatbots')
    #         return []
    #     else:
    #         chatbot = self.chatbots[ip]
    #         return chatbot.qa_pairs

    def get_generator(self, ip, question):
        if ip not in self.chatbots:
            # raise ValueError(f'ip: {ip} not in chatbots')
            return []
        else:
            chatbot = self.chatbots[ip]
            generator = chatbot.query_stream(question)
            return generator

    def pop_qa_pairs(self, ip):
        """不清空，知识将has_new_pair设置为False"""
        if ip not in self.chatbots:
            return []
        else:
            chatbot = self.chatbots[ip]
            qa_pairs = chatbot.qa_pairs
            chatbot.has_new_pair = False
            return qa_pairs

    def create_new_chatbot(self):
        chatbot = HChatBot()
        # chatbot = FakeChatGPT()
        return chatbot

    def query(self, ip, text):
        """
        text: request txt.
        """
        chatbot = self.get_bot_by_ip(ip, create_new=True)

        if not self._stream:
            answer = chatbot.query(text)
            chatbot.append_qa(text, answer)
            chatbot.has_new_pair = True
            return redirect(url_for("index", result=answer))
        else:
            generator = chatbot.query_stream(text)
            
            return redirect(url_for("index", result='query_stream', lastq=text))
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

    def write_log(self, ip, text, query_once='query once', answer=''):
        self.query_count += 1
        timet = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # query_once = 'query once' if query_once else ''
        context = f'[{timet}] {query_once}. ip: {ip}, text: {text}, count: {self.query_count}'
        context += f', answer: {answer}' if answer else ''
        logger.info(context)
        save_file = f'{logg_dir}/query.log'
        # 手动写入日志，save_path为日志文件路径，日志文件正在被使用
        while True:
            try:
                with open(save_file, 'a') as f:
                    f.write(context + '\n')
                break
            except Exception as e:
                # logger.error(f'write log error: {e}')
                time.sleep(1)
         

class ErrorHandler:
    
    """
    error类型：
    openai.error.RateLimitError， 点击速率太快
    """

