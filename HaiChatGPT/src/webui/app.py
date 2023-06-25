import os, sys
import time
import openai
import logging
import damei as dm
import traceback
from pathlib import Path
from flask import Flask, redirect, render_template, request, url_for, Response, stream_with_context
from flask import render_template_string
from flask import session, jsonify
from flask_cors import CORS
from werkzeug.middleware.dispatcher import DispatcherMiddleware

logger = dm.get_logger('app')

app = Flask(__name__)
app.secret_key = '123456'  # 设置Session密钥，用于加密Session数据
app.config['SESSION_PERMANENT'] = False # 设置session是否永久有效
app.config['SESSION_USE_SIGNER'] = True # 设置是否对session进行签名

#app.config['APPLICATION_ROOT'] = '/chatapi' # 设置应用的根路径

#def simple(env, resp):
#    resp(b'200 OK', [(b'Content-Type', b'text/plain')])
#    return [b'Hello WSGI World']

#app.wsgi_app = DispatcherMiddleware(simple, {'/chatapi': app.wsgi_app})

# 设置跨域
# CORS(app, resources={r"/*": {"origins": "http://example.com"}})
CORS(app)

from .utils.web_object import WebObject
webo = WebObject()

from .utils.app_routes import *
from .utils.api_routes import *
from .utils.auth import *
from .utils import general

@app.route("/", methods=("GET", "POST"))
def index():
    print(f'收到index请求: {request}. method: {request.method}')
    
    user = general.get_user_from_session()
    chatbot = webo.get_bot_by_username(user, create_if_no_exist=False)

    if request.method == "POST":
        return render_template("index.html", username=user)

    elif request.method == "GET":
        if chatbot is not None:
            # 开启历史聊天记录
            chatbot.show_history = True
            chatbot.show_last_question = True

        return render_template("index.html", username=user)
    else:
        raise ValueError(f'unknown method: {request.method}')
    
@app.route('/login-dialog.html')
def login_dialog():
    # 检测到是其他网站发起的，需要保存referer
    try:
        callback = request.args.get('callback')
        logger.info(f'login-dialog.html请求的data为: {callback}')
        if callback is not None:
            session['callback'] = callback
    except:
        pass
    
    logger.info(f'login-dialog.html session: {session}')
    return render_template('login-dialog.html')


@app.route('/user-info.html')
def user_info():
    return render_template('user-info.html')

@app.route('/ip_addr')
def ip_addr():
    # print(f'收到ip请求， {request}')
    # logger.debug(f'收到ip请求， {request}')
    ret = f"data: {request.remote_addr}\n\n"
    # print(f'返回ip响应: {ret}')
    return Response(ret, mimetype="text/event-stream")


@app.route('/clear', methods=['GET', 'POST'])
def clear():
    user = general.get_user_from_session()
    webo.delete_convo_and_save(user, convo_id='default')  # 删除chatbot
    return jsonify({'success': True, 'message': '清空成功'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    logger.debug(f'login请求的data为: {data}')
    username = data.get('username')
    password = data.get('password')
    ok, msg = webo.user_mgr.verify_user(username, password)
    if ok:
        session['username'] = username
        # session['logged_users'] = session.get('logged_users', []) + [username]
        message =  {'success': True, 'message': '登录成功', 'username': session['username']}
    else:
        message = {'success': False, 'message': msg}

    # 检测到是其他网站发起的登录请求，需要重定向到其他网站，并返回用户名    
    if 'callback' in session:
        callback = session.pop('callback', None)
        # 重定向到其他网站，并返回用户名
        access_token = "hatbot_access_token"
        secret_key = app.secret_key
        token = jwt.encode({'username': username, 'access_token': access_token}, secret_key, algorithm='HS256')
        # TODO: 这里需要修改，不能直接返回token
        session['access_token'] = access_token
        logger.info(f'重定向到其他网站: {callback}?username={username}&token={token}')
        callback_url = (f'{callback}?username={username}&token={token}')
        message["url"] = callback_url

    return jsonify(message)

        
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    # user_name = request.get_json().get('username')
    user_name = general.get_user_from_session(msg='logout')
    if user_name is None:
        return jsonify({'success': False, 'message': '用户未登录'})
    # session['username'] = None
    session.pop('username', None)
    ret = {'success': True, 'message': f'{user_name} 登出成功', 'redirect': False, 'url': None}

    # 退出登录后，退出oauth，重定向到主页
    access_token = session.get('access_token')
    logger.debug(f'access_token: {access_token}')
    if webo.user_mgr.use_sso_auth and access_token is not None:
        session.pop('access_token', None)
        session.pop('refresh_token', None)
        aouth_logout_url = "https://login.ihep.ac.cn/logout"
        home_url = url_for('index', _external=True)
        
        full_url = f"{aouth_logout_url}?WebServerURL={home_url}"
        ret['redirect'] = True
        ret['url'] = full_url
        logger.info(f"full_url: {full_url}")
        return jsonify(ret)
    else:
        # 不进行重定向
        pass
    
    logger.debug(f'logout返回: {ret}')
    return jsonify(ret)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    logger.info(f'register请求的data为: {data}')
    username = data.get('username')
    password = data.get('password')
    phone = data.get('phone')

    if webo.user_mgr.is_exist(username):
        return {'success': False, 'message': f'用户名{username}已存在'}
    else:
        webo.user_mgr.add_user(username, password, phone=phone)
        return jsonify({'success': True, 'message': '注册成功'})

def run(**kwargs):
    # from gevent import pywsgi
    # from geventwebsocket.handler import WebSocketHandler
    # server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    # server.serve_forever()
    
    work_dir = kwargs.get('work_dir', os.getcwd())
    here = os.path.dirname(os.path.abspath(__file__))
    # os.chdir(here)

    # setup UserManager
    use_sso_auth = kwargs.get('use_sso_auth',False)
    use_sql = kwargs.get('use_sql', False)
    if use_sql:
        from .utils.user_manager_sql import UserManagerSQL
        user_mgr = UserManagerSQL()
        # 连接到MySQL数据库
        # app.config.from_pyfile('app_config.py')
        app.config.from_pyfile(user_mgr.app_sql_config)
        from .utils.user_manager_sql import db as db
        db.app = app
        db.init_app(app)
        with app.app_context():
            #db.drop_all()
            db.create_all()
            user_mgr.save_user_to_sql()
    else:
        from .utils.user_manager import UserManager
        user_mgr = UserManager()
    user_mgr.use_sso_auth = use_sso_auth


    # setup web object
    webo.user_mgr = user_mgr

    host = kwargs.get('host', '127.0.0.1')
    port = kwargs.get('port', 5000)
    debug = kwargs.get('debug', False)
    app.run(host=host, port=port, debug=debug)
    # socketio.run(app, host=host, port=port, debug=debug)

    os.chdir(work_dir)


if __name__ == "__main__":
    run(debug=True)
    






