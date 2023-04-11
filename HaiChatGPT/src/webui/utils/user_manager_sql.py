import os, sys
from pathlib import Path
import damei as dm
import json
from ....version import __appname__
import time
from datetime import datetime
from .user_manager import UserManager

logger = dm.getLogger('user_manager')

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm.attributes import flag_modified
db = SQLAlchemy()

import uuid

# 定义用户模型
class UserData(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(80), default='public', unique=True, nullable=True)
    password = db.Column(db.String(80))
    phone = db.Column(db.Integer)
    email = db.Column(db.String(80))
    auth_type = db.Column(db.String(80))
    cookies = db.Column(JSON, nullable=False, default={})
    uuid = db.Column(db.String(32))

    chats = db.relationship('UserChat', backref='name', lazy=True)
    histories = db.relationship('UserHistory', backref='name', lazy=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# 定义历史记录模型
class UserHistory(db.Model):
    __tablename__ = 'histories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    username = db.Column(db.String(200))
    convo_id = db.Column(db.String(200), default='default')
    role = db.Column(db.String(200), default='user')
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

    role = db.Column(db.String(200), default='user')
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 监听UserData类的before_delete事件，删除chat
@event.listens_for(UserData, 'before_delete')
def delete_user_posts(mapper, connection, target):
    UserChat.query.filter_by(user_id=target.id).delete()

# 监听UserChat类的before_delete事件，删除message
@event.listens_for(UserChat, 'before_delete')
def delete_user_posts(mapper, connection, target):
    UserMessage.query.filter_by(chat_id=target.id).delete()

class UserManagerSQL(UserManager):
    def __init__(self, use_sso_auth=False) -> None:
        super().__init__(use_sso_auth)
        self.sql_config_file = f'{Path.home()}/.{__appname__}/app_sql_config.py'

    @property
    def app_sql_config(self):
        file_path = self.sql_config_file
        if os.path.exists(file_path):
            return file_path
        else:
            content = 'SQLALCHEMY_DATABASE_URI = '
            x = input(f"请输入数据库地址，(例如：mysql://xxx@localhost/xxx):\n")
            content += f'"{x}"\n'
            logger.info(f'set app_sql_config to {content}')
            with open(file_path, 'w') as f:
                f.write(content)
            return file_path

    def read_users_from_file(self):
        pass

    def read_cookies_from_file(self):
        pass

    def save_users_to_file(self, users):
        pass

    def save_file(self, file_path, data):
        pass

    def get_user_info(self, user):
        return UserData.query.filter_by(name=user).first().as_dict()
    
    def add_user(self, user, password=None, **kwargs):
        one_user = dict()
        one_user['password'] = password
        one_user['auth_type'] = kwargs.get('auth_type', 'local')
        one_user['uuid'] = uuid.uuid4().hex
        one_user.update(kwargs)

        # 添加用户到数据库中
        if not UserData.query.filter_by(name=user).first():
            user_data = UserData(name=user)
            for key, value in one_user.items():
                try:
                    setattr(user_data, key, value)
                except KeyError:
                    print(f"KeyError: {user_data},{key},{value}")
            db.session.add(user_data)
            db.session.commit()
        else:
            logger.info(f"User {user} 存在.")

    def remove_user(self, user):
        # 从数据库中删除用户
        # TODO 现在是只删除用户，不删除历史记录
        user_data = UserData.query.filter_by(name=user).first()
        if user_data:
            db.session.delete(user_data)
            db.session.commit()
            logger.info(f"User {user} 已被删除.")
        else:
            logger.info(f"User {user} 不存在.")

    def verify_user(self, user, password, **kwargs):
        use_sso_auth = kwargs.get('use_sso_auth', self.use_sso_auth)
        
        user_data = UserData.query.filter_by(name=user).first()
        if user_data is None:
            if  use_sso_auth:
                logger.debug(f'Local auth failed, try sso auth.')
                ok, msg = self.sso_verify_user(user, password, **kwargs)
                if ok:
                    self.add_user(user, password, auth_type='sso')
                    return True, ''
                else:
                    return False, f'本地用户不存在，统一认证用户验证失败，请尝试注册。msg: {msg}'
            else:
                return False, f'本地用户不存在，请尝试注册。msg: {msg}'
        else:
            if user_data.password == password:
                return True, ''
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
                    return False, '本地用户密码错误'
    
    def is_exist(self, user):
        return UserData.query.filter_by(name=user).first() is not None
    
    def is_admin(self, user):
        user_data = UserData.query.filter_by(name=user).first()
        if user_data is None:
            return False
        else:
            return user_data.auth_type == "admin"
    
    def is_plus(self, user):
        user_data = UserData.query.filter_by(name=user).first()
        if user_data is None:
            return False
        if self.is_admin(user):
            return True
        return user_data.auth_type == "plus"
    
    def get_cookie(self, user):
        user_data = UserData.query.filter_by(name=user).first()
        return user_data.cookies if user_data else None

    def write_cookie(self, user, **kwargs):
        user_data = UserData.query.filter_by(name=user).first()
        if user_data is None:
            raise Exception(f'User {user} not exist!')
        
        one_cookies = user_data.cookies
        one_cookies.update(kwargs)
        user_data.cookies = one_cookies
        # 重要，sqlalchemy无法检测JSON变化，必须人工设置变化标识
        flag_modified(user_data, "cookies")
        db.session.commit()

        logger.debug(f'Write cookie for user {user}: {one_cookies}')

    def save_history(self, username, convo_id, one_entry):
        # logger.debug(f'Save history for user {user}: {one_entry}')
        # 搜索用户
        user_data = UserData.query.filter_by(name=username).first()
        if not user_data:
            user_data = UserData.query.filter_by(name="public").first()
            # TODO 每次会话创建有一个唯一ID的临时用户
            if not user_data:
                user_data = UserData(name="public")
                db.session.add(user_data)
                db.session.commit()

        '''
        # 保存 chat
        chat = UserChat.query.filter_by(user_id=user.id, chat=convo_id).first()
        if not chat:
            chat = UserChat(user_id=user.id, chat=convo_id)
            db.session.add(chat)
            db.session.commit()

        # 保存 Message
        message = UserMessage(
            chat_id=chat.id, role=one_entry["role"], content=one_entry["content"])
        db.session.add(message)
        db.session.commit()
        '''

        # 保存历史记录
        user_history = UserHistory(
            username=username,
            convo_id=convo_id,
            role=one_entry["role"],
            content=one_entry["content"],
            user_id=user_data.id)
        db.session.add(user_history)
        db.session.commit()

    def get_permission_level(self, user):
        user_data = UserData.query.filter_by(name=user).first()
        if not user_data:  # 未登录
            return 0
        elif user_data.auth_type == 'public':  # public
            return 1
        else:
            if self.is_admin(user):  # admin
                return 4
            elif self.is_plus(user):  # plus
                return 3
            else:
                return 2  # 登录
            

    def get_chat_and_message(self,user_name: str, chat_name='default'):
        user = UserData.query.filter_by(name=user_name).first()
        if not user:
            logger.info(f"用户 {user_name} 不存在")

        chat = UserChat.query.filter_by(
            user_id=user.id, chat=chat_name).first()
        if not chat:
            logger.info(f"会话 {chat_name} 不存在")

        # 读取Message
        # messages = UserMessage.query.filter_by(chat_id=chat.id).all()
        # messages = UserMessage.query.filter(UserMessage.chat_id == chat.id).all()
        # 这两个语句会报错，未知原因
        messages = db.session.query(UserMessage).filter_by(chat_id=chat.id).all()

        result = []
        for message in messages:
            result.append({'role': message.role, 'content': message.content})
        return result
    
