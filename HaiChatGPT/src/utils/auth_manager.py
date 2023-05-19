"""
进行多个账号的授权管理，每个账号对应有1个API_KEY和1个ACCESS_TOKEN
"""

import yaml
import os, sys
from pathlib import Path
import shutil
import damei as dm
from collections import OrderedDict
from ...version import __appname__

logger = dm.get_logger('auth_manager')

class AuthLevel:
    """权限等级"""
    UNLOGIN = 0
    PUBLIC = 1
    LOGGED_IN = 2
    PLUS = 3
    ADMIN = 4


class AuthManager:
    def __init__(self):
        self.config_path = f'{Path.home()}/.{__appname__}/auth.yaml'
        self.config = self.read_config()
        """{'username': {'access-token': '', 'api-key': ''}}"""

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
    
    @property
    def users_with_api_key(self):
        """有api-key的用户列表"""
        valid_users = []
        for user, info in self.config.items():
            if 'api-key' not in info.keys():
                continue
            if info['api-key'] != '':
                valid_users.append(user)
        return valid_users
    
    @property
    def users_with_access_token(self):
        """有access-token的用户列表"""
        valid_users = []
        for user, info in self.config.items():
            if 'access-token' not in info.keys():
                continue
            if info['access-token'] != '':
                valid_users.append(user)
        return valid_users
    
    def read_config(self):
        
        if not os.path.exists(self.config_path):
            self.create_empty_config(self.config_path)
            self.read_config()
        with open(self.config_path, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        return config

    @property
    def access_token_url(self):
        return "https://chat.openai.com/api/auth/session"
    
    @property
    def api_key_url(self):
        return "https://platform.openai.com/account/api-keys"
    
    def save_config(self, config_path, config):
        comments = [
            "##\n# Authorized info format:",
            "# - username: # (your email) ",
            "#     api-key: ''  # (your api key, can be found at https://platform.openai.com/account/api-keys)",
            "#     access-token: ''  # (your access token, can be found at https://chat.openai.com/api/auth/session)",
            "#     paid: False  # (set True if you are ChatGPT Plus user)",
            "# - username2: # (another email)",
            "#      ...",
            "# Just one of api-key and access-token is needed.\n##\n\n"
        ]
        comments = "\n".join(comments)
        with open(config_path, 'w') as f:
            f.write(comments)
            yaml.dump(config, f,  default_flow_style=False)
        logger.info(f"Config saved to {config_path}")

        test = False
        if test:
            with open(config_path, 'r') as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
            print(config)

    def create_empty_config(self, config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        empty_config = dict()
        empty_config['<username>'] = {"access-token": "", "api-key": "", "paid": False}
        self.save_config(config_path, empty_config)

    def get_user_by_api_key(self, api_key):
        for user, info in self.config.items():
            if info['api-key'] == api_key:
                return user
        return None
    
    def get_user_by_access_token(self, access_token):
        for user, info in self.config.items():
            if info['access-token'] == access_token:
                return user
        return None
    
    def get_paid_by_api_key(self, api_key):
        user = self.get_user_by_api_key(api_key)
        if user is None:
            return False
        elif 'paid' not in self.config[user].keys():
            return False
        return self.config[user]['paid']
    
    def get_paid_by_access_token(self, access_token):
        user = self.get_user_by_access_token(access_token)
        if user is None:
            return False
        elif 'paid' not in self.config[user].keys():
            return False
        return self.config[user]['paid']

    def get_api_key(self, username):
        return self.config[username]['api-key']
    
    def get_api_keys(self):
        return [self.get_api_key(user) for user in self.users_with_api_key]
    
    def get_access_token(self, username):
        return self.config[username]['access-token']
    
    def get_access_tokens(self):
        return [self.get_access_token(user) for user in self.users_with_access_token]
        
    def get_one_api_key(self):
        """
        获取API Key，如果没有则提示输入，如果有多个则提示选择
        TODO: 根据动态负载均衡获取api-key
        """
        users_with_api_key = self.users_with_api_key
        api_keys = [self.get_api_key(user) for user in users_with_api_key]
        if len(api_keys) == 0:
            print(f"\nPlease input your API Key (can be found here {self.api_key_url}): ")
            api_key = input()
            print("\nPlese input your username (can be any string):")
            username = input()
            assert username != '', "Username can't be empty!"
            if username in self.config.keys():
                self.config[username]['api-key'] = api_key
            else:
                new_user = {username: {'api-key': api_key, 'access-token': ''}}
                self.config.update(new_user)
            self.save_config(self.config_path, self.config)
            return api_key
        elif len(api_keys) == 1:
            return api_keys[0]
        else:
            print('Please select your API Key: ')
            for i, api_key in enumerate(api_keys):
                user = users_with_api_key[i]
                idx_lenth = len(str(len(api_keys)))
                lenth = max([len(xx) for xx in users_with_api_key])
                print(f"  ({i+1:>{idx_lenth}}) {user:>{lenth}}'s API-KEY: {api_key[:5]}{'*' * (len(api_key) - 10)}{api_key[-5:]}")
            index = int(input())
            return api_keys[index - 1]
        
    def get_one_access_token(self):
        """
        获取Access Token，如果没有则提示输入，如果有多个则提示选择
        """
        users_with_access_token = self.users_with_access_token
        access_tokens = [self.get_access_token(user) for user in users_with_access_token]
        if len(access_tokens) == 0:
            print(f"\nPlease input your Access Token (can by found here: {self.access_token_url}): ")
            access_token = input()
            print("\nPlese input your username (can be any string):")
            username = input()
            assert username != '', "Username can't be empty!"
            if username in self.config.keys():
                self.config[username]['access-token'] = access_token
            else:
                new_user = {username: {'api-key': '', 'access-token': access_token}}
                self.config.update(new_user)
            self.save_config(self.config_path, self.config)
            return access_token
        elif len(access_tokens) == 1:
            return access_tokens[0]
        else:
            print('Please select your Access Token: ')
            for i, access_token in enumerate(access_tokens):
                user = users_with_access_token[i]
                idx_lenth = len(str(len(access_tokens)))
                lenth = max([len(xx) for xx in users_with_access_token])
                print(f"  ({i+1:>{idx_lenth}}) {user:>{lenth}}'s Access Token: {access_token[:5]}{'*'*10}{access_token[-5:]}")
            index = int(input())
            return access_tokens[index - 1]
        

