
import os

from flask import redirect, url_for, make_response, session, request, flash, jsonify
import requests
from flask import Response, stream_with_context
from flask_cors import cross_origin
import jwt


import damei as dm
import traceback

from ..app import app, webo
from .user_manager import PremisionLevel
from . import general

logger = dm.get_logger('api_routes')

# api 服务
@app.route('/api/redirect')
def api_redirect():
    if 'callback' in session:
        callback = session.pop('callback', None)
        # 重定向到其他网站，并返回用户名
        logger.info(f'/api/redirect: 重定向到其他网站: {callback}')
        return redirect(f'{callback}')
    else:
        return redirect('/')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    logger.debug(f'login请求的data为: {data}')
    username = data.get('username')
    password = data.get('password')
    callback = data.get('callback', None)
    session['callback'] = callback

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

@app.route('/api/logout')
def api_logout():
    '''
    接受从其他网站发起退出登录请求，
    本地退出，
    统一认证退出，
    重定向到原网站。
    '''
    callback = request.args.get('callback', None)
    jwt_token = request.args.get('token', None)
    logger.info(f'api_logout: {request.headers}')

    cookie= request.cookies
    logger.info(f'cookie_username: {cookie}')

    # TODO 验证token, 防止伪造请求
    try:
        data = jwt.decode(jwt_token, app.secret_key, algorithms=['HS256'])
        username = data.get('username', None)
        access_token = data.get('access_token', None)
        logger.debug(f"data: {data}")
    except Exception as e:
        logger.error(f"token解析失败: {e}")
        res = make_response(callback)
        res.set_cookie('username', '', expires=0)
        return Response('token解析失败', status=400)

    logger.info(f'/api/logout callback: {callback}')

    if username is None:
        logger.error(f'username is None')
        return Response('username is None', status=400)
    
    if access_token is None:
        logger.error(f'access_token is None')
        return Response('access_token is None', status=400)
    
    if callback is None:
        logger.error(f'callback is None')
        return Response('callback is None', status=400)
    
    # 退出登录
    if access_token != session.get('access_token'):
        logger.error(f'access_token不一致，可能是伪造的请求')               
        logger.error(f'token: {access_token}, session[access_token]: {session.get("access_token")}')
        return Response('access_token不一致，可能是伪造的请求', status=400)

    session.pop('username', None)    
    session.pop('access_token', None)

    # 如果使用umt认证，退出umt
    if webo.user_mgr.use_sso_auth:
        oauth_logout_url = "https://login.ihep.ac.cn/logout"
        full_url = f"{oauth_logout_url}?WebServerURL={callback}"
        logger.info(f"/api/logout full_url: {full_url}")
        return redirect(full_url)

    return redirect(callback)   



@app.route('/api/test', methods=['POST', 'GET'])
def api_test():
    return jsonify({'status': 'ok'})



@app.route('/api/<method>', methods=['POST', 'GET'])
def api_method(method):
    # jwt_token = request.headers.get('Authorization', None)
    # jwt_data = jwt.decode(jwt_token, app.secret_key, algorithms=['HS256'])
    logger.info(f'api_method: {method}')
    # logger.info(f'request headers: {request.headers}')
    token = request.headers.get('Authorization', None)
    logger.info(f'token: {token}')
    
    try:
        data = request.get_json()
        logger.info(f'收到请求: {data}')
    except Exception as e:
        pass

    username = request.args.get('username', None)
    try:
        username = data.pop('username', username)
    except Exception as e:
        pass

    if username is None:
        return Response('username is None', status=400)
    logger.info(f'username: {username}')

    # 验证token
    hepai_api_key = os.environ.get('HEPAI_API_KEY')
    assert hepai_api_key is not None, 'You must provide an `API_KEY` in the `Authorization` header.'
    headers={"Authorization": f"Bearer {hepai_api_key}"}
    
    response = requests.post(
    url=f'http://aiapi.ihep.ac.cn:42901/admin',
    headers=headers,
    json={
        'function': 'verify_access_token',
        "access_token": token,
    },)

    token_verify = response.json()
    if token_verify['success'] is False:
        return Response('token is invalid', status=400)
    logger.info(f'rep.json: {response.json()}')
    if token_verify['message'] != username:
        return Response('username is not match', status=400)

    # chat 功能
    
    if method == 'completions':        
        data = request.get_json()

        logger.info(f'收到completions请求: {data}')
        # print(f'data: {data}')
        # TODO 现阶段的处理方式是，从messages中获取最后一个message，利用现有的方法控制bot，进行历史对话的缓存
        # TODO 后续计划修改hai-next的接口，直接传入prompt，而不是message
        prompt = data['messages'][-1]['content']

        params = data.get('params', {})
        webo.query(username, prompt, **params)
        stream_buffer = webo.get_stream_buffer(username)

        def Api_stream():
            # stream 输出完后，添加一个结束标志
            text0 = "data: "
            count = 0
            for i,line in enumerate(stream_buffer):
                # 只输出最后一个字符，即最后一个
                text1 = line                
                line = text1.replace(text0,"")
                
                text0 = text1.replace("\n\n","")
            
                yield f"data: {line}"
                yield f"id: {count}\n\n"
                yield f"event: message\n\n"

                count = count + 1

            line = "[DONE]"
            logger.info(f'line: {line}')
            yield f'data: {line}\n\n'
            yield f"id: {count}\n\n"
            yield f"event: message\n\n"

        stream = Api_stream()

        if stream is None:
            ret = f"data: [DONE]\n\n"
        else:
            ret = stream
        logger.info(f'ret: {ret}')

        return Response(ret, mimetype="text/event-stream")
    
    if method == 'history':
        try:
            data = request.get_json()
        except Exception as e:
            data = {}

        length = data.get('length', 50)

        one_convo = webo.get_history(username)
        
        if one_convo is None:
            one_convo = ""

        qa_list = one_convo.split("<|im_bbbr|>")

        # 构建目标列表
        result_list = []
        for i, item in enumerate(qa_list):
            # 根据索引值 i 来确定 "role" 字段的值
            qa = item.replace("<|im_br|>","\n")
            qa = item.split("<|im_sep|>")

            if len(qa) != 2:
                continue
            result_list.append({"role": "user", "content": qa[0], "created_at": ""})
            result_list.append({"role": "assistant", "content": qa[1],"created_at": ""})


        chats_sessions = webo.user_mgr.get_history(username,length=length)

        # TODO 旧版本one_convo只有一个session，新版本预计有多个session，需要修改
        # default session 中插入 one_convo
        # for session in chats_sessions:
        
        if 'default' not in chats_sessions:
            chats_sessions['default'] = []

        chats_sessions['default'] = chats_sessions['default'] + result_list
        for message in chats_sessions['default']:
            message['content'] = message['content'].replace("<|im_br|>","\n")

        # print(chats_sessions['default'] )

        logger.debug(f'收到get_user_session请求: user: {username}')
        # logger.info(f'chats_sessions: {chats_sessions}')
        return jsonify({'success': True, 'message': username, "sessions": chats_sessions})

    if method == "test":
        return jsonify({'success': True, 'message': "test"})
