import os, sys
from pathlib import Path
import damei as dm
import json
from ....version import __appname__


logger = dm.getLogger('user_manager')


class UserManager(object):
    def __init__(self, use_sso_auth=False) -> None:
        self._users_file = f'{Path.home()}/.{__appname__}/users.json'
        self._users = self.read_users_from_file()
        self._sso_auth = None
        self.use_sso_auth = use_sso_auth

    @property
    def sso_auth(self):
        if self._sso_auth is None:
            from ...utils.sso_oauth import SSOAuth
            self._sso_auth = SSOAuth()
        return self._sso_auth

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

    def verify_user(self, user, password, **kwargs):
        logger.info(f'Try local auth. all users: {self._users}')
        if user in self._users.keys():
            is_ok = self._users[user]['password'] == password
            if is_ok:
                return True
            else:
                pass
        else:
            pass
        
        logger.info(f'Locak auth failed, try sso auth.')
        use_sso_auth = kwargs.get('use_sso_auth', self.use_sso_auth)
        if use_sso_auth:
            ret = self.sso_auth.verify_user(user, password)
            if ret:
                # logger.info(f'{user} ssoauth verify user success!')
                return True
            else:
                # logger.info(f'{user} ssoauth verify user failed!')
                return False
    
    def is_exist(self, user):
        return user in self._users.keys()
