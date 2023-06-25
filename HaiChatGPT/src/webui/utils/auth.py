import os
from pathlib import Path
import json
from typing import Any
from ....version import __appname__

from flask import redirect, url_for, make_response, session, request, flash, jsonify
from functools import wraps
from authlib.integrations.flask_client import OAuth
from authlib.integrations.requests_client import OAuth2Session

import jwt
# from authlib import Config
# from authlib.oauth2.rfc6749 import Config

from ..app import app, webo
from ..utils import general
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
            },
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

    # TODO 需要重写
    def token_required(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')

            if not token:
                return jsonify({'message': 'No token provided'}), 401

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                #current_user = User.query.filter_by(id=data['id']).first()
                current_user = None
            except:
                return jsonify({'message': 'Invalid token'}), 401

            return f(current_user, *args, **kwargs)

        return decorated

ihepAuth = IHEPAuth()

@app.route('/login_sso')
def login_sso():
    # redirect_uri = 'http://192.168.68.22:5555/callback'
    redirect_uri = url_for('callback', _external=True)
    logger.info(f"redirect_uri: {redirect_uri}")
    authorize_redirect = oauth.ihep.authorize_redirect(redirect_uri)
    logger.info(f"authorize_redirect: {authorize_redirect.headers}")
    return authorize_redirect

@app.route('/api/login_sso', methods=['GET'])
def api_login_sso():
    # redirect_uri = 'http://192.168.68.22:5555/callback'
    callback = request.args.get('callback', None)

    if callback is None:
        return jsonify({'message': 'No callback provided'}), 401
    else:
        session['callback'] = callback

    redirect_uri = url_for('callback', _external=True)
    logger.info(f"redirect_uri: {redirect_uri}")
    authorize_redirect = oauth.ihep.authorize_redirect(redirect_uri)
    logger.info(f"authorize_redirect: {authorize_redirect.headers}")
    locaton = authorize_redirect.headers.get('Location')

    logger.info(f"callback: {session['callback']}")

    return jsonify({'location': locaton})
    return authorize_redirect.headers.get('Location')

@app.route('/callback', methods=['GET', 'POST'])
def callback():
    # TODO 原则上ihep.authorize_access_token应该能自动配置client_secret和client_id
    # 但是这里需要手动配置，否则会报错
    try:
        token_info = oauth.ihep.authorize_access_token(
            client_secret=ihepAuth.config['client_secret'],
            client_id=ihepAuth.config['client_id'],
        )
        ok = True
    except Exception as e:
        logger.error(e)
        return redirect('/login-dialog.html')
    
    token = token_info['access_token']
    userInfo = json.loads(token_info['userInfo'])  
    username = userInfo['cstnetId']
    password = userInfo['password']
    umtId = userInfo['umtId']
    refreshToken = token_info['refresh_token']
    expiert_in = token_info['expires_in']
    expires_at = token_info['expires_at']
    
    # 保存访问令牌
    session['username'] = username
    session['umtId'] = umtId
    session['access_token'] = token
    session['refresh_token'] = refreshToken

    logger.info(f'oauth for ihep callback, umtId: {umtId}')
    # 保存用户信息
    webo.user_mgr.add_user(username, password, phone=None, auth_type='sso')

    if ok:
        msg = jsonify({'success': True, 'message': '登录成功', 'username': session['username']})
    else:
        msg = jsonify({'success': False, 'message': '登录失败'})

    # 检测到是从其他网站跳转过来的，需要重定向到其他网站，并返回用户名
    if 'callback' in session:
        callback = session.pop('callback', None)
        # 重定向到其他网站
        secret_key = app.secret_key
        token = jwt.encode({'username': username, 'access_token': token}, secret_key, algorithm='HS256')
        
        logger.info(f'重定向到其他网站: {callback}')
        logger.info(f'username:{username}, token:{token}')
        # 将 token 存储在 Cookie 中
        data = jsonify({'username': username, 'token': token})

        response = make_response(redirect(f'{callback}?username={username}&token={token}') )
        response.headers['Access-Control-Allow-Origin'] = '*'
        # 添加 auth
        # response.headers.add("authorization",token)
        # response.set_cookie('token', token)

        # logger.info(f'response: {response.headers}')
        
        return response

    # 重定向到主页
    return redirect('/') 
