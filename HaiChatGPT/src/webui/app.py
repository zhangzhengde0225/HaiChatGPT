import os, sys
import time
import openai
import logging
import damei as dm
import traceback
# import queue
from pathlib import Path
from flask import Flask, redirect, render_template, request, url_for, Response
# os.environ['LOGGING_LEVEL'] = str(logging.DEBUG)

logger = dm.get_logger('app')

app = Flask(__name__)
from .web_object import WebObject
webo = WebObject()


@app.route("/", methods=("GET", "POST"))
def index():
    print(f'收到index请求: {request}. method: {request.method}')
    # ip = request.remote_addr
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    chatbot = webo.get_bot_by_ip(ip, create_new=False)
    print(f'ip: {ip}. bot: {chatbot}')

    if request.method == "POST":
        text = request.form["prompt"]  # this is the query
        text = '你是谁？' if text == '' else text
        
        print(f'text: {text} ')
        chatbot = webo.get_bot_by_ip(ip, create_new=True)
        chatbot.show_history = True
        chatbot.show_last_question = True
        chatbot.show_last_answer = True

        chatbot.last_question = text
        lastq = text
        lasta = chatbot.query_stream(text)  # it's a generator
        
        webo.write_log(ip, text)
        
        return render_template("index.html", result=lasta, lastq=lastq)
        return webo.query(ip, text)

    elif request.method == "GET":
        if chatbot is not None:
            # 开启历史聊天记录
            chatbot.show_history = True
            chatbot.show_last_question = False
            chatbot.show_last_answer = False
            lastq = chatbot.last_question if chatbot.show_last_question else None
            lasta = chatbot.last_answer if chatbot.show_last_answer else None
        else:
            lastq = None
            lasta = None

        return render_template("index.html", result=lastq, lasta=lasta)
    else:
        raise ValueError(f'unknown method: {request.method}')

    result = request.args.get("result")
    # result = None
    # result = '你好'
    return render_template("index.html", result=result)

@app.route('/ip_addr')
def ip_addr():
    # print(f'收到ip请求， {request}')
    ret = f"data: {request.remote_addr}\n\n"
    # print(f'返回ip响应: {ret}')
    return Response(ret, mimetype="text/event-stream")

@app.route('/qa_pairs')  # question and 
def qa_pairs():
    # ip = request.remote_addr
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    chatbot = webo.get_bot_by_ip(ip, create_new=False)
    # print(f'收到qa_pairs请求， {request}, ip: {ip}, chatbot: {chatbot}')
    logger.debug(f'收到qa_pairs请求， {request}, ip: {ip}, chatbot: {chatbot}')
    
    if chatbot is None:
        data = '<|im_end|>'
    elif chatbot.show_history:  # True or False
        qa_pairs = chatbot.qa_pairs  # 还有可能是空的
        print(f'qa_pairs: {qa_pairs}')
        if qa_pairs == [] or qa_pairs is None:
            data = '<|im_end|>'
        else:
            data = '<|im_br|>'.join([f'{q}<|im_sep|>{a}' for q, a in qa_pairs])
            chatbot.show_history = False  # 读取一次后，关闭
    else:
        data = '<|im_end|>'
    ret = f"data: {data}\n\n"
    # print(f'返回qa_pairs响应: {ret}')
    logger.debug(f'返回qa_pairs响应: {ret}')
    return Response(ret, mimetype="text/event-stream")


@app.route('/stream')
def stream():  # 即获取流式的last_answer
    # ip = request.remote_addr
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    chatbot = webo.get_bot_by_ip(ip, create_new=False)
    # print(f'收到stream请求， {request}, ip: {ip}, chatbot: {chatbot}')
    logger.debug(f'收到stream请求， {request}, ip: {ip}, chatbot: {chatbot}')
    if chatbot is None:
        ret = f"data: <|im_end|>\n\n"
    elif chatbot.show_last_answer:  
        # 每次收到post请求后，都会设置为True, 收到get请求后，设置为False
        # 此处处理完后，设置为False
        lastq = chatbot.last_question
        lasta = 'stream'  # 用于标记是stream的回答
        logger.debug(f'请求stream的show_last_answser为True, lastq = {lastq}')
        if lasta is None or lasta == '':
            ret = f"data: <|im_end|>\n\n"
        else:
            assert chatbot.last_question != '', 'last_question is empty'
            generator = webo.get_generator(ip, lastq)
            ret = generator
            chatbot.show_last_answer = False
    else:  # TODO
        ### 存在chatbot但是由不显示last_answer的情况
        ### 是指
        lastq = chatbot.last_question
        lasta = chatbot.last_answer
        print(f'请求stream2: lastq = {lastq}, lasta = {lasta}')
        # print(f'保存')
        if lastq is not None and lasta is not None:
            chatbot.append_qa(lastq, lasta)  # 保存到历史记录中
            webo.write_log(ip, lastq, query_once='', answer=lasta)
        chatbot.last_question = None
        chatbot.last_answer = None
        
        ret = f"data: <|im_end|>\n\n"
        # return Response(generator, mimetype="text/event-stream")
    # print(f'返回stream响应: {ret}')
    logger.debug(f'返回stream响应: {ret}')
    return Response(ret, mimetype="text/event-stream")

@app.route('/clear', methods=['GET', 'POST'])
def clear():
    # ip = request.remote_addr
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    # chatbot = webo.get_bot_by_ip(ip, create_new=False)
    print(f'收到clear请求， {request}, ip: {ip}')
    # 删除chatbot
    webo.delete_bot_by_ip(ip)
    ret = f"data: <|im_end|>\n\n"
    print(f'返回clear响应: {ret}')
    return render_template("index.html", result=None, lastq=None)

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

    os.chdir(work_dir)


if __name__ == "__main__":
    run(debug=True)
    






