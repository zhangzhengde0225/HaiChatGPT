
import os, sys
from pathlib import Path
import shutil
import json
import damei as dm

from ..version import __appname__
logger = dm.get_logger('runner')


class Runner(object):

    def __init__(self, opt):
        self.opt = opt

        # 读取api_key和token的功能
        self.config_path = f'{Path.home()}/.{__appname__}/config.json'
        self.config = self.read_config()
        self._current_api_key = None
        self._current_access_token = None

    @property
    def current_api_key(self):
        if self._current_api_key is None:
            self._current_api_key = self.get_one_api_key()
        return self._current_api_key
    
    @property
    def current_access_token(self):
        if self._current_access_token is None:
            self._current_access_token = self.get_one_access_token()
        return self._current_access_token

    def read_config(self):
        use_api_key = self.opt.use_api_key
        config_path = self.config_path
        if use_api_key:
            if not os.path.exists(config_path):  # 不存在就创建
                self.create_empty_config(config_path)
                self.read_config()
            else:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                api_keys = config['api_keys']
                if len(api_keys) == 0:
                    print("Please input your API Key: ")
                    api_key = input()
                    config['api_keys'].append(api_key)
                    self.save_config(config_path, config)
                    return config
                else:
                    return config
        else:
            if not os.path.exists(config_path):
                self.create_empty_config(config_path)
                self.read_config()
            else:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                access_tokens = config['access_tokens']
                if len(access_tokens) == 0:
                    print("No Access Token found, For more info: https://github.com/zhangzhengde0225/HaiChatGPT).\nPlease input your Access Token: ")
                    access_token = input()
                    config['access_tokens'].append(access_token)
                    self.save_config(config_path, config)
                    return config
                else:
                    return config

    def save_config(self, config_path, config):
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Config saved to {config_path}")

    def create_empty_config(self, config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        empty_config = {
            "access_tokens": [],
            "api_keys": [],
            }
        with open(config_path, 'w') as f:
            json.dump(empty_config, f, indent=4)

    def get_one_api_key(self):
        api_keys = self.config['api_keys']
        if len(api_keys) == 0:
            print('Please input your API Key: ')
            api_key = input()
            self.config['api_keys'].append(api_key)
            self.save_config(self.config_path, self.config)
            return api_key
        elif len(api_keys) == 1:
            return api_keys[0]
        else:
            print('Please select your API Key: ')
            for i, api_key in enumerate(api_keys):
                print(f"{i + 1}. {api_key[:5]}{'*' * (len(api_key) - 10)}{api_key[-5:]}")
            index = int(input())
            return api_keys[index - 1]
        
    def get_one_access_token(self):
        access_tokens = self.config['access_tokens']
        if len(access_tokens) == 0:
            print('Please input your Access Token: ')
            access_token = input()
            self.config['access_tokens'].append(access_token)
            self.save_config(self.config_path, self.config)
            return access_token
        elif len(access_tokens) == 1:
            return access_tokens[0]
        else:
            print('Please select your Access Token: ')
            for i, access_token in enumerate(access_tokens):
                print(f"{i + 1}. {access_token[:5]}{'*' * 10}{access_token[-5:]}")
            index = int(input())
            return access_tokens[index - 1]

    def run_cli(self):
        """Run the command line interface."""
        
        # 需要把日志级别设置为WARNING，否则会打印很多无用的信息
        import logging
        os.environ['LOGGING_LEVEL'] = str(logging.WARNING)

        from .cli.cli import cli_main, cli_main_token
        if self.opt.use_api_key:
            from ..apis import API_ChatBot as Chatbot
            api_key = self.current_api_key
            chatbot = Chatbot(
                    api_key=api_key,
                    proxy=self.opt.proxy,
                    engine=self.opt.engine)
            cli_main(chatbot)
        else:
            from ..apis import Token_ChatBot as Chatbot
            config={}
            config["access_token"] = self.current_access_token
            if self.opt.proxy is not None:
                config["proxy"] = self.opt.proxy
            chatbot = Chatbot(
                    config=config,
                    conversation_id=None, 
                    parent_id=None,
                    session_client=None,
                    lazy_loading=False,
                    )

            cli_main_token(chatbot)

    def run_webui(self):
        """Run the web interface."""
        opt = self.opt

        # 参数：host, port, debug, use_api_key, proxy, engine

        from .webui.app import webo

        if opt.debug:  # use fake bot
            from .webui.fake_bot import FakeChatGPT
            webo.uninstantiated_chatbot = FakeChatGPT
            webo.params_for_instantiation = {
                'max_qa': 5,
            }
        elif opt.use_api_key:
            from .chatbots.hai_chat_bot import HChatBot
            webo.uninstantiated_chatbot = HChatBot
            webo.params_for_instantiation = {
                'api_key': self.current_api_key,
                'engine': opt.engine,
                'proxy': opt.proxy,
                'temperature': opt.temperature,
                }
        else:
            from .chatbots.hai_chat_bot_token import HTokenChatBot
            webo.uninstantiated_chatbot = HTokenChatBot
            config = {}
            config["access_token"] = self.current_access_token
            if opt.proxy is not None:
                config["proxy"] = opt.proxy
            config["paid"] = False  # whether this is a plus account
            webo.params_for_instantiation = {
                "config": config,
                'conversation_id': None,
                'parent_id': None,
                'session_client': None,
                'lazy_loading': False,
                'temperature': opt.temperature,
                'max_qa': 5,
                }
        
        from .webui.app import run as run_app
        run_app(
            host=self.opt.host,
            port=self.opt.port,
            debug=self.opt.debug,
        )

    
    @staticmethod
    def run_gui():
        """Run the GUI interface."""
        from ..apis import gui_main
        gui_main()



def run(mode, opt, **kwargs):
    runner = Runner(opt)

    if opt.cli:
        runner.run_cli()
    elif opt.gui:
        runner.run_gui()
    elif opt.webui:
        runner.run_webui()
    else:
        raise ValueError("No mode selected.")




