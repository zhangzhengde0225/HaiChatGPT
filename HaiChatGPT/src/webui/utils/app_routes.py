

from flask import request, jsonify
from flask import Response, stream_with_context

import damei as dm
import traceback


from ..app import app, webo
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

@app.route('/testxx', methods=['POST'])
def testxx():
    data = request.get_json()
    logger.debug(f'收到test请求: {data}')

