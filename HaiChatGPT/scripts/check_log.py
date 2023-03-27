



"""
用来统计用户数量，每个用户的提问数目和答案等数据。
"""
import os, sys
from pathlib import Path
import damei as dm
import json
# from HaiChatGPT.apis import __appname__
# from ..version import __appname__
__appname__ = 'HaiChatGPT'


class CheckLog(object):
    def __init__(self) -> None:
        self.logs_dir = f'{Path.home()}/.{__appname__}'
        pass

    def __call__(self):
        self.check_users()
        self.check_user_cookies()
        pass

    def _load_json(self, json_file):
        with open(json_file, 'r') as f:
            return json.load(f)
        
    def check_user_cookies(self):
        cookies_file = f'{self.logs_dir}/users_cookie.json'
        if not os.path.exists(cookies_file):
            raise FileNotFoundError(f'users_cookie.json not found in {self.logs_dir}')
        cookies_data = self._load_json(cookies_file)
        print(f'共计用户数: {len(cookies_data)}')
        user_has_api_key = []
        users_history_count = {}
        total_count = 0
        for user, cookie in cookies_data.items():
            # print(user, cookie.keys())
            if user not in users_history_count.keys():
                users_history_count[user] = 0
            if 'api_key' in cookie.keys():
                user_has_api_key.append(user)
            if 'history_convos' in cookie.keys():
                convos = cookie['history_convos']
                # print(convos.keys())
                for conv_name, conv_data in convos.items():
                    # print(f'用户{user}的对话{conv_name}的数据: {conv_data}')
                    for i, conv in enumerate(conv_data):
                        role = conv['role']
                        if role == 'user':
                            pass
                        elif role == 'assistant':
                            users_history_count[user] += 1
                            total_count += 1
        print(f'共计{len(user_has_api_key)}个用户有api_key: {user_has_api_key}')

        info = dm.misc.dict2info(users_history_count)        
        print(f'共计{len(users_history_count)}个用户有{total_count}个历史对话:\n{info}')


    def check_users(self):
        users_file = f'{self.logs_dir}/users.json'
        if not os.path.exists(users_file):
            raise FileNotFoundError(f'users.json not found in {self.logs_dir}')
        users_data = self._load_json(users_file)
        print(f'共计用户数: {len(users_data)}')
        
        users_type_local = 0
        users_type_sso = 0
        for k, v in users_data.items():
            if v['auth_type'] == 'local':
                users_type_local += 1
            elif v['auth_type'] == 'sso':
                users_type_sso += 1
            else:
                users_type_local += 1
                # raise ValueError(f'Unknown auth_type: {v["auth_type"]}')
        print(f'本地用户数: {users_type_local}')
        print(f'单点登录用户数: {users_type_sso}')


if __name__ == '__main__':
    cl = CheckLog()
    cl()
