
import os, sys
from pathlib import Path
import shutil
import json
import damei as dm

from ..version import __appname__
from .utils.auth_manager import AuthManager
logger = dm.get_logger('runner')


class Runner(object):

    def __init__(self, opt):
        self.opt = opt
        self.auth_manager = AuthManager()
    
    def run_cli(self):
        """Run the command line interface."""
        opt = self.opt
        # 需要把日志级别设置为WARNING，否则会打印很多无用的信息

        from .cli.cli import cli_main, cli_main_token, cli_main_35

        if opt.use_fake_bot:  # use fake bot
            from .webui.fake_bot import FakeChatGPT
            chatbot = FakeChatGPT()
            cli_main_token(chatbot)
        elif self.opt.use_api_key:
            # from ..apis import API_ChatBot as Chatbot
            from ..apis import API_ChatBot_35 as Chatbot  # need proxy
            from .utils.check_network import check_network
            api_key = self.auth_manager.current_api_key
            user = self.auth_manager.get_user_by_api_key(api_key)
            logger.debug(f"use {user}'s api_key: {api_key[:5]}{'*'*(len(api_key)-10)}{api_key[-5:]}")
            chatbot = Chatbot(
                    api_key=api_key,
                    engine=opt.engine,
                    proxy=self.opt.proxy,
                    max_tokens=3000,
                    temperature=0.5,
                    )
            check_network(chatbot, timeout=5)
            cli_main_35(chatbot, proxy=self.opt.proxy)
        else:
            from ..apis import Token_ChatBot as Chatbot
            config={}
            config["access_token"] = self.auth_manager.current_access_token
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

        if opt.debug:
            import logging
            os.environ['LOGGING_LEVEL'] = str(logging.DEBUG)

        from .webui.app import webo

        if opt.use_fake_bot:  # use fake bot
            from .webui.fake_bot import FakeChatGPT
            webo.uninstantiated_chatbot = FakeChatGPT
            webo.params_for_instantiation = {
                'max_qa': 5,
            }
        elif opt.use_api_key:
            # from .chatbots.hai_chat_bot import HChatBot  # deprecated at 20230307
            from .chatbots.hai_chat_bot_35 import HChatBot
            from .utils.check_network import check_network
            webo.uninstantiated_chatbot = HChatBot
            api_key = self.auth_manager.current_api_key

            webo.params_for_instantiation = {
                'api_key': api_key,
                'engine': opt.engine,
                'proxy': opt.proxy,
                "max_tokens": 3000,
                'temperature': opt.temperature,
                }
            
            chatbot = HChatBot(**webo.params_for_instantiation)
            check_network(chatbot, timeout=5)
            del chatbot
        else:
            from .chatbots.hai_chat_bot_token import HTokenChatBot
            webo.uninstantiated_chatbot = HTokenChatBot
            config = {}
            config["access_token"] = self.auth_manager.current_access_token
            user = self.auth_manager.get_user_by_access_token(config["access_token"])
            if opt.proxy is not None:
                config["proxy"] = opt.proxy
            # config["paid"] = False  # whether this is a plus account
            config["paid"] = self.auth_manager.get_paid_by_access_token(config["access_token"])
            logger.debug(f"Run on HTokenChatBot with {user}'s Access Token, paid={config['paid']}.")
            webo.params_for_instantiation = {
                "config": config,
                'conversation_id': None,
                'parent_id': None,
                'session_client': None,
                'lazy_loading': False,
                # 'temperature': opt.temperature,
                'max_qa': 5,
                }
        
        from .webui.app import run as run_app
        from .webui.app import user_mgr
        user_mgr.use_sso_auth = opt.use_sso_auth
        
        run_app(
            host=self.opt.host,
            port=self.opt.port,
            debug=self.opt.use_fake_bot,
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




