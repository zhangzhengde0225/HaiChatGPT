
import os, sys
import time
import damei as dm
from flask import Flask, redirect, render_template, request, url_for
from flask import Response
import requests
from ..app import app
from ....version import __appname__
from ..fake_bot import FakeChatGPT
from .file_manager import FileManager

import logging
from pathlib import Path


logg_dir = f'{Path.home()}/.{__appname__}/logs'
if not os.path.exists(logg_dir):
    os.makedirs(logg_dir)
save_path = f'{logg_dir}/webui.log'
handler = logging.FileHandler(save_path)

logger = dm.getLogger('web_object')

class WebObject(object):
    """
    与web对象交互，强绑定
    """
    def __init__(self, **kwargs) -> None:
        self.file_mgr = FileManager()
        self._stream = True
        """
        为适应不同username的请求，不同的username需要不同的chatbot
        """
        self.chatbots = dict()  # key: username, value: chatbot
        self.query_count = 0
        self.user_mgr = kwargs.get('user_mgr', None)
        logger.debug(f'WebObject: user_mgr: {self.user_mgr}')

        self.uninstantiated_chatbot = FakeChatGPT  # default bot
        self.params_for_instantiation = {}
    
    def get_bot_by_username(self, username, create_if_no_exist=True):
        if username not in self.chatbots:
            if create_if_no_exist:
                chatbot = self.create_new_chatbot()
                self.chatbots[username] = chatbot
                return chatbot
            else:
                return None
        else:
            chatbot = self.chatbots[username]
            return chatbot
        
    def set_tmp_sys_prompt(self, username, sys_prompt):
        chatbot = self.get_bot_by_username(username, create_if_no_exist=True)
        chatbot.tmp_sys_prompt = sys_prompt

    def delete_convo_and_save(self, username, convo_id = 'default', **kwargs):
        """
        删除当前的chat，并保存到数据库中
        """
        if username not in self.chatbots:
            return
        else:
            chatbot = self.chatbots[username]
            one_convo = chatbot.conversation.get(convo_id, None)  # 其实一个chat
            if one_convo is None:
                return
            else:
                for i in range(len(one_convo)-1):
                    entry = one_convo[i+1]  # 不要系统的第一句
                    self.user_mgr.save_history(username, convo_id, entry)
                chatbot.reset(convo_id=convo_id, **kwargs)

    def pop_qa_pairs(self, username):
        """不清空，只是将has_new_pair设置为False"""
        if username not in self.chatbots:
            return []
        else:
            chatbot = self.chatbots[username]
            qa_pairs = chatbot.qa_pairs
            chatbot.has_new_pair = False
            return qa_pairs

    def create_new_chatbot(self):
        chatbot = self.uninstantiated_chatbot(
            **self.params_for_instantiation
        )
        return chatbot

    def query(self, username, text):
        """
        根据用户名获取bot，然后query_stream, 返回就保存在bot.stream_buffer中
        """
        chatbot = self.get_bot_by_username(username, create_if_no_exist=True)

        """
        用户设置的缓存信息
        """
        user_cookie = self.user_mgr.get_cookie(username)
        if user_cookie is not None:
            # 修改chatbot的参数
            self.set_bot_params(chatbot, **user_cookie)  # 根据cookie设置chatbot的参数
        
        # logger.debug(f'Username: {username}, user_cookie: {user_cookie}')
        logger.info(f'webo chatbots: {len(self.chatbots)} {self.chatbots.keys()}')

        stream = chatbot.query_stream(
            text, 
            user_mgr=self.user_mgr, 
            user_name=username,
            webo = self,
            )
        chatbot._stream_buffer = stream
        return stream
    
    def set_bot_params(self, chatbot, **params):
        for k, v in params.items():
            if hasattr(chatbot, k):  # 存在
                if chatbot.__getattribute__(k) != v:  # 不等于
                    chatbot.__setattr__(k, v)

    def get_stream_buffer(self, username):
        chatbot = self.get_bot_by_username(username, create_if_no_exist=False)
        if chatbot is None:
            # logger.debug('exist bots:', self.chatbots)
            logger.debug(f'username: {username} not in chatbots')
            return None
            # raise ValueError(f'username: {username} not in chatbots')
        else:
            return chatbot.stream_buffer
        
    def get_history(self, username, convo_id='default'):
        chatbot = self.get_bot_by_username(username, create_if_no_exist=False)
        if chatbot is None:
            logger.debug(f'username: {username} not in chatbots')
            return None
            # raise ValueError(f'username: {username} not in chatbots')
        else:
            return chatbot.get_history(convo_id=convo_id, username=username, user_mgr=self.user_mgr)
    
    def render(self, ret, **kwargs):
        return redirect(url_for("index", result=ret))

    def write_log(self, username, text, query_once='query once', answer=''):
        self.query_count += 1
        timet = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # query_once = 'query once' if query_once else ''
        context = f'[{timet}] {query_once}. username: {username}, text: {text}, count: {self.query_count}'
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

    

