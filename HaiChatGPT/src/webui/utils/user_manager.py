import os, sys
from pathlib import Path
import damei as dm
import json
from ....version import __appname__

logger = dm.getLogger('user_manager')


class UserManager(object):
    def __init__(self) -> None:
        self._users_file = f'{Path.home()}/.{__appname__}/users.json'
        self._users = self.read_users_from_file()

    def read_users_from_file(self):
        if not os.path.exists(self._users_file):
            os.makedirs(os.path.dirname(self._users_file), exist_ok=True)
            empty_dict = dict()
            self.save_users_to_file(empty_dict)
            return empty_dict
        else:
            with open(self._users_file, 'r') as f:
                return json.load(f)
            
    def save_users_to_file(self, users):
        with open(self._users_file, 'w') as f:
            json.dump(users, f, indent=4)

    @property
    def users(self):
        return self._users
    
    def add_user(self, user, password, **kwargs):
        one_user = dict()
        one_user['password'] = password
        one_user.update(kwargs)
        self._users[user] = one_user
        # TODO: 保存到文件中
        self.save_users_to_file(self._users)

    def remove_user(self, user):
        del self._users[user]

    def verify_user(self, user, password):
        logger.info(f'all users: {self._users}')
        if user in self._users.keys():
            return self._users[user]['password'] == password
        else:
            return False
    
    def is_exist(self, user):
        return user in self._users.keys()
