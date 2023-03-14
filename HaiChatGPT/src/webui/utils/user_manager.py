import os, sys
from pathlib import Path
import damei as dm
import json
from ....version import __appname__
import time
from datetime import datetime

logger = dm.getLogger('user_manager')

from ..app import db

# 定义用户模型
class UserData(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(80), default='guest', unique=True, nullable=True)
    password = db.Column(db.String(80))
    phone = db.Column(db.Integer)
    email = db.Column(db.String(80))
    auth_type = db.Column(db.String(80))
    api_key = db.Column(db.String(80))
    cookies = db.Column(db.String(200))
    
    chats = db.relationship('UserChat', backref='name', lazy=True)
    histories = db.relationship('UserHistory', backref='name', lazy=True)
    config = db.relationship('UserConfig', backref='name', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.name

# TODO 用户-设置
class UserConfig(db.Model):
    __tablename__ = 'configs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    temperature = db.Column(db.Float)
    engine = db.Column(db.String(80))
    api_key = db.Column(db.String(80))
    proxy = db.Column(db.String(80))
    max_tokens = db.Column(db.Float)

# 定义历史记录模型
class UserHistory(db.Model):
    __tablename__ = 'histories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    role = db.Column(db.String(200), default='user')
    convo_id = db.Column(db.String(200), default='default')   
    query = db.Column(db.Text)
    text = db.Column(db.Text)
    status = db.Column(db.String(80), default='default')

# 将历史记录和会话分开保存
# 用户-会话-信息
# 用户-历史记录
class UserChat(db.Model):
    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    chat = db.Column(db.String(80), default='default', nullable=False)
    messages = db.relationship('UserMessage', backref='chat', lazy=True)

class UserMessage(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)

    query = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(80), default='default')

class UserManager(object):
    def __init__(self, use_sso_auth=False) -> None:
        self._users_file = f'{Path.home()}/.{__appname__}/users.json'
        self._users_cookie_file = f'{Path.home()}/.{__appname__}/users_cookie.json'
        self._users = self.read_users_from_file()
        self._cookies = self.read_cookies_from_file()
        self._sso_auth = None  # 初始化为None，只有在使用sso_auth时才会初始化
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
            
    def read_cookies_from_file(self):
        file_path = self._users_cookie_file
        if not os.path.exists(file_path):   
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            empty_dict = dict()
            self.save_file(file_path, empty_dict)
            return empty_dict
        else:
            with open(file_path, 'r') as f:
                return json.load(f)
            
    def save_users_to_file(self, users):
        with open(self._users_file, 'w') as f:
            json.dump(users, f, indent=4)
            
    def save_file(self, file_path, data):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    @property
    def users(self):
        return self._users
    
    @property
    def cookies(self):
        return self._cookies
    
    def get_user_info(self, user):
        return self.users[user]
    
    def add_user(self, user, password=None, **kwargs):
        one_user = dict()
        one_user['password'] = password
        one_user['auth_type'] = kwargs.get('auth_type', 'local')
        one_user.update(kwargs)
        self._users[user] = one_user
        # TODO: 保存到文件中
        # self.save_users_to_file(self._users)

    def remove_user(self, user):
        del self._users[user]

    def verify_user(self, user, password, **kwargs):
        # logger.info(f'Try local auth. all users: {self._users}')
        use_sso_auth = kwargs.get('use_sso_auth', self.use_sso_auth)
        
        # 寻找本地的数据库
        # 如果没有，尝试用sso验证,
        # 如果有，用本地验证, 再尝试用sso验证
        # TODO 还没有修改密码功能
        user_data = UserData.query.filter_by(name=user).first()
        if user_data is None and use_sso_auth:
            logger.info(f'Local auth failed, try sso auth.')
            ok, msg = self.sso_verify_user(user, password, **kwargs)
            if ok:
                user_data = UserData(name=user, password=password, auth_type='sso')
                db.session.add(user_data)
                db.session.commit()
                return True, ''
            else:
                return False, f'本地用户不存在，统一认证用户验证失败，请尝试注册。msg: {msg}'
        else:
            if user_data.auth_type == 'sso' and use_sso_auth:
                ok, msg = self.sso_verify_user(user, password, **kwargs)
                if ok:
                    user_data.password = password
                    db.session.commit()
                    return True, ''
                else:
                    return False, f'统一认证用户失败'
            else:
                if user_data.password == password:
                    return True, ''
                else:
                    return False, '本地用户密码错误'

        '''
        logger.info(f'Local auth failed, try sso auth.')
        if use_sso_auth:
            ok, msg = self.sso_verify_user(user, password, **kwargs)
            if ok:
                return True, ''
            else:
                return False, f'本地和统一认证用户均失败，请尝试注册。msg: {msg}'
        return False, '本地用户不存在'
        '''

    def sso_verify_user(self, user, password, **kwargs):
        ok, msg = self.sso_auth.verify_user(user, password)
        logger.debug(f'SSO auth result: {ok}, {msg}')
        if ok:
            # logger.info(f'{user} ssoauth verify user success!')
            # 在本地保存用户信息，下次直接使用本地验证
            if user not in self._users.keys():
                self.add_user(user, password, auth_type='sso')
            return True, ''
        else:
            # logger.info(f'{user} ssoauth verify user failed!')
            return False, msg
    
    def is_exist(self, user):
        return user in self._users.keys()
    
    def is_admin(self, user):
        if user not in self._users.keys():
            return False
        return self._users[user].get('is_admin', False)
    
    def is_plus(self, user):
        if user not in self._users.keys():
            return False
        if self.is_admin(user):  # admin一定是plus
            return True
        return self._users[user].get('is_plus', False)
    
    def get_cookie(self, user):
        return self._cookies.get(user, None)
    
    def write_cookie(self, user, **kwargs):
        if user not in self._users.keys():
            raise Exception(f'User {user} not exist!')
        if user not in self._cookies.keys():
            self._cookies[user] = dict()
        self._cookies[user].update(kwargs)
        logger.debug(f'Write cookie for user {user}: {self._cookies[user]}')
        self.save_file(self._users_cookie_file, self._cookies)

    def save_history(self, user, convo_id, one_entry):
        # logger.debug(f'Save history for user {user}: {one_entry}')
        if user not in self._users.keys():
            pass
        if user not in self._cookies.keys():
            self._cookies[user] = dict()
        if 'history_convos' not in self._cookies[user].keys():
            # print('history_convos not in cookies')
            self._cookies[user]['history_convos'] = dict()
        if convo_id not in self._cookies[user]['history_convos'].keys():
            # print('convo_id not in cookies')
            self._cookies[user]['history_convos'][convo_id] = list()
        # self._cookies[user]['history'].append(one_entry)
        # print(self._cookies[user]['history_convos'][convo_id])
        one_entry['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self._cookies[user]['history_convos'][convo_id].append(one_entry)
        self.save_file(self._users_cookie_file, self._cookies)
        
        
