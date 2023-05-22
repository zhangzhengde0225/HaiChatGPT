import os
from pathlib import Path
import json
from typing import Any
from ....version import __appname__

from flask import redirect, url_for, session, request, flash
from authlib.integrations.flask_client import OAuth
from authlib.integrations.requests_client import OAuth2Session
# from authlib import Config
# from authlib.oauth2.rfc6749 import Config

from ..app import app, webo
import damei as dm

logger = dm.get_logger('oauth2')

oauth = OAuth()
oauth.init_app(app)


class IHEPAuth:
    def __init__(self):
        self.confit_path = f'{Path.home()}/.{__appname__}/app_oauth_config.json'
        self.set_up_config()
        self.register()

    def set_up_config(self):
        file_path = self.confit_path
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                config = json.load(f)

            logger.info(f'app_oauth_config: {file_path}')
            logger.info(f'set app_oauth_config from {config}')
        else:
            client_id = input(f"请输入client_id:\n")
            client_secret = input(f"请输入client_secret:\n")
            authorize_url = 'https://login.ihep.ac.cn/oauth2/authorize'
            access_token_url = 'https://login.ihep.ac.cn/oauth2/token'
            theme = input(f"请输入theme:\n")
            redirect_uri = input(f"请输入redirect_uri:\n")
            
            config = {
                'client_id': client_id,
                'client_secret': client_secret,
                'authorize_url': authorize_url,
                'access_token_url': access_token_url,
                'authorize_params': {
                    'theme': theme,
                    'redirect_uri': redirect_uri,
                }   
            }

            with open(file_path, 'w') as f:
                json.dump(config, f, indent=4)
                
            logger.info(f'set app_oauth_config to {config}')
        self.config = config

    def register(self):
        oauth.register(
            name='ihep',
            client_id= self.config['client_id'],
            client_secret=self.config['client_secret'],
            authorize_url=self.config['authorize_url'],
            access_token_url=self.config['access_token_url'],
            authorize_params={
                'theme': self.config['authorize_params']['theme'],
                'redirect_uri': self.config['authorize_params']['redirect_uri'],
            }
        )

    def verify_user(self, username, password, **kwargs):
        """验证用户"""
        # TODO 验证用户
        return True, ''

    # TODO 需要重写
    def checkLogin(self, responce):
        """检查用户是否登录"""
        if responce.status_code == 401:
            new_token = oauth.ihep.refresh_token(session['refresh_token'])
            session['refresh_token'].update(new_token)
            flash('Token refreshed', 'success')
            return redirect(url_for('protected_resource'))
        else:
            return responce.json()

ihepAuth = IHEPAuth()

@app.route('/login_sso')
def login_sso():
    # redirect_uri = 'http://192.168.68.22:5555/callback'
    redirect_uri = url_for('callback', _external=True)
    logger.info(f"redirect_uri: {redirect_uri}")
    return oauth.ihep.authorize_redirect(redirect_uri)

@app.route('/callback', methods=['GET', 'POST'])
def callback():
    logger.info("oauth.ihep callback")
    
    logger.info( oauth.ihep.client_secret  )
    # TODO 原则上ihep.authorize_access_token应该能自动配置client_secret和client_id
    token_info = oauth.ihep.authorize_access_token( 
                        client_secret = oauth.ihep.client_secret, 
                        client_id=oauth.ihep.client_id 
                    )
    
    token = token_info['access_token']
    userInfo = json.loads(token_info['userInfo'])
    logger.info(userInfo)
    
    username = userInfo['cstnetId']
    password = userInfo['password']
    umtId = userInfo['umtId']
    refreshToken = token_info['refresh_token']
    expiert_in = token_info['expires_in']
    expires_at = token_info['expires_at']
    
    logger.info(f"token: {token}")
    # 保存访问令牌
    session['username'] = username
    session['umtId'] = umtId
    session['access_token'] = token
    session['refresh_token'] = refreshToken

    logger.info(userInfo)

    # 保存用户信息
    webo.user_mgr.add_user(username, password, phone=None)

    # 重定向到主页
    return redirect('/')

@app.route('/logout_sso')
def logout_sso():
    session.pop('username', None)
    session.pop('access_token', None)
    session.pop('refresh_token', None)
    return redirect('/')

