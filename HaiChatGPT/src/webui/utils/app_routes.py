

from flask import request, jsonify
from flask import Response, stream_with_context

import damei as dm
import traceback


from ..app import app, webo
from .user_manager import PremisionLevel
from . import general

logger = dm.get_logger('app_routes')


@app.route('/send_prompt', methods=['POST'])
def send_prompt():
    data = request.get_json()
    prompt = data['message']
    prompt = 'sysc help' if prompt == '' else prompt
    user = general.get_user_from_session()
    logger.debug(f'收到send_prompt请求: user: {user}, prompt: {prompt}')

    # 由webo来处理不同用户的请求:
    try:
        webo.query(user, prompt)  # 得到回答保存在用户的chatbot的stream_buffer中
        chatbot = webo.get_bot_by_username(user, create_if_no_exist=False)
        chatbot.show_history = True
    except Exception as e:
        error_info = f'webo.query error: {e}. Traceback: {traceback.format_exc()}'
        logger.error(f'{error_info}')
        return jsonify({'success': False, 'message': error_info})
    return jsonify({'success': True, 'message': prompt})

@app.route('/stream')
def stream(**kwargs):  # 即获取流式的last_answer
    user = general.get_user_from_session()
    logger.debug(f'收到stream请求: Method: {request.method}. User: {user}. Kwargs: {kwargs}')
    stream_buffer = webo.get_stream_buffer(user)
    # logger.debug(f'stream_buffer: {stream_buffer}')
    if stream_buffer is None:
        ret = f"data: <|im_end|>\n\n"
    else:
        ret = stream_buffer
    logger.debug(f'ret: {ret}')
    return Response(ret, mimetype="text/event-stream")
    return Response(stream_with_context(ret), mimetype="text/event-stream")

@app.route('/qa_pairs')  # question and 
def qa_pairs():
    # 
    # return Response(f"data: <|im_end|>\n\n", mimetype="text/event-stream")

    user = general.get_user_from_session()
    chatbot = webo.get_bot_by_username(user, create_if_no_exist=False)
    if chatbot is None:
        data = '<|im_end|>'
        return Response(f"data: {data}\n\n", mimetype="text/event-stream")
    if not chatbot.show_history:
        # print('chatbot.show_history is False')
        data = '<|im_end|>'
        return Response(f"data: {data}\n\n", mimetype="text/event-stream")
    # logger.debug(f'收到qa_pairs请求: Method: {request.method}. User: {user}. chatbot: {chatbot}')
    # logger.debug(f'chatbot.show_history: {chatbot.show_history}')
    history = webo.get_history(user)
    if history == [] or history is None:
        data = '<|im_end|>'
    else:
        data = history
        chatbot.show_history = False

    ret = f"data: {data}\n\n"
    # logger.debug(f'返回qa_pairs响应: {ret}')
    return Response(ret, mimetype="text/event-stream")


@app.route('/get_username', methods=['GET'])
def get_username():
    user = general.get_user_from_session()
    # logger.debug(f'收到get_username请求: user: {user}')
    return jsonify({'success': True, 'username': user})

@app.route("/get_user_data")
def get_user_data():
    """样例数据:
    user_data = {
        "username": "public",
        "phone": "13112345678",
        "phone_verified": True,
        "email": "zhangsan@example.com",
        "user_type": "free",
        "usage": 5,
        "limit": 10,
        "group": None,
        "group_admin": False,
        "group_members": None,
    }
    """
    user = general.get_user_from_session()
    # logger.debug(f'收到get_user_data请求: user: {user}')
    user_data = webo.user_mgr.get_user_data(user)
    result = {'success': True, 'user_data': user_data}
    return jsonify(result)

@app.route('/upload', methods=['POST'])
def upload():
    """通过XMLHttpRequest上传文件"""
    user = general.get_user_from_session()
    logger.debug(f'收到upload请求: user: {user}')
    # 限制权限为plus及以上
    if webo.user_mgr.user_level(user) < PremisionLevel.PLUS:
        return jsonify({'success': False, 'message': f'您是{webo.user_mgr.user_level_str(user)}用户，需要PLUS或使用个人API_KEY'})
    # 保存文件，解析文件，返回内容和TOKENS
    content, num_tokens = webo.file_mgr.process_uploaded_file(
        request=request, username=user)
    if num_tokens >= 1500:
        return jsonify({'success': False, 'message': f'内容{num_tokens}Tokens，超过1500个限制'})
    # 设置临时的prompt
    webo.set_tmp_sys_prompt(user, content)
    return jsonify({'success': True, 'message': num_tokens})

@app.route('/delete_tmp_sys_prompt', methods=['GET'])
def delete_tmp_sys_prompt():
    user = general.get_user_from_session()
    # logger.debug(f'收到delete_tmp_sys_prompt请求: user: {user}')
    # webo.delete_tmp_sys_prompt(user)
    chatbot = webo.get_bot_by_username(user, create_if_no_exist=False)
    chatbot.tmp_sys_prompt = None
    return jsonify({'success': True})


@app.route('/testxx', methods=['POST'])
def testxx():
    data = request.get_json()
    logger.debug(f'收到test请求: {data}')



