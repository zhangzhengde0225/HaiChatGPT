import os, sys
import time
import openai
import logging
import damei as dm
import traceback
from pathlib import Path
from flask import Flask, redirect, render_template, request, url_for, Response, stream_with_context
from flask import session, jsonify

logger = dm.get_logger('app')

app = Flask(__name__)
app.secret_key = 'this_is_bxx_session_key'  # 设置Session密钥，用于加密Session数据


from .utils.user_manager import UserManager
user_mgr = UserManager()
from .utils.web_object import WebObject
webo = WebObject(user_mgr=user_mgr)



from .utils.app_routes import *
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
    return render_template('login-dialog.html')


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
    webo.delete_convo_and_save(user)  # 删除chatbot
    return jsonify({'success': True, 'message': '清空成功'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    logger.debug(f'login请求的data为: {data}')
    username = data.get('username')
    password = data.get('password')
    ok, msg = user_mgr.verify_user(username, password)
    if ok:
        session['username'] = username
        # session['logged_users'] = session.get('logged_users', []) + [username]
        return jsonify({'success': True, 'message': '登录成功', 'username': session['username']})
    else:
        return {'success': False, 'message': msg}
        
    
@app.route('/logout', methods=['POST'])
def logout():
    # user_name = request.get_json().get('username')
    user_name = general.get_user_from_session(msg='logout')
    if user_name is None:
        return jsonify({'success': False, 'message': '用户未登录'})
    # session['username'] = None
    session.pop('username', None)
    ret = {'success': True, 'message': f'{user_name} 登出成功'}
    logger.debug(f'logout返回: {ret}')
    return jsonify(ret)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    logger.info(f'register请求的data为: {data}')
    username = data.get('username')
    password = data.get('password')
    phone = data.get('phone')

    if user_mgr.is_exist(username):
        return {'success': False, 'message': f'用户名{username}已存在'}
    else:
        user_mgr.add_user(username, password, phone=phone)
        return jsonify({'success': True, 'message': '注册成功'})



def run(**kwargs):
    # from gevent import pywsgi
    # from geventwebsocket.handler import WebSocketHandler
    # server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    # server.serve_forever()
    
    work_dir = kwargs.get('work_dir', os.getcwd())
    here = os.path.dirname(os.path.abspath(__file__))
    # os.chdir(here)

    # setup web object

    host = kwargs.get('host', '127.0.0.1')
    port = kwargs.get('port', 5000)
    debug = kwargs.get('debug', False)
    app.run(host=host, port=port, debug=debug)
    # socketio.run(app, host=host, port=port, debug=debug)

    os.chdir(work_dir)


if __name__ == "__main__":
    run(debug=True)
    






