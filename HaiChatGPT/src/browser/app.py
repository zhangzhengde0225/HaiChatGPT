import os, sys
import time
import openai
import logging
import damei as dm
import queue
from flask import Flask, redirect, render_template, request, url_for, Response
os.environ['LOGGING_LEVEL'] = str(logging.DEBUG)
logger = dm.get_logger('app')

app = Flask(__name__)
from .web_object import WebObject
webo = WebObject()

@app.route("/", methods=("GET", "POST"))
def index():
    print(f'req: {request}. method: {request.method}')
    
    if request.method == "POST":
        text = request.form["prompt"]  # this is the query
        ip = request.remote_addr
        if text == '':
            text = '你是谁？'
        print(f'ip: {ip}, text: {text} ')
        return webo.query(ip, text)

    result = request.args.get("result")
    # result = None
    # result = '你好'
    return render_template("index.html", result=result)

@app.route('/stream')
def stream(flag='0'):
    print(f'收到stream请求， {request} flag: {flag}')
    # def generate():
    #     for i in range(2):
    #         yield f"data: {i}{flag}\n\n"
    #         time.sleep(0.2)
    #     yield f"data: <|im_end|>\n\n"
    # return Response(generate(), mimetype="text/event-stream")

    ip = request.remote_addr
    text = 'xx'
    generator = webo.get_generator(ip, text)
    return Response(generator, mimetype="text/event-stream")

@app.route('/ip_addr')
def ip_addr():
    # print(f'收到ip请求， {request}')
    ret = f"data: {request.remote_addr}\n\n"
    return Response(ret, mimetype="text/event-stream")

@app.route('/qa_pairs')  # question and 
def qa_pairs():
    print(f'收到qa_pairs请求， {request}')
    ip = request.remote_addr
    if webo.has_new_pair(ip=ip):
        qa_pairs = webo.get_qa_pairs(ip)  # a list of tuple
        webo.chatbots[ip].has_new_pair = False
        data = '<|im_br|>'.join([f'{q}<|im_sep|>{a}' for q, a in qa_pairs])
        # print(f'qa_pairs: {qa_pairs}, type: {type(qa_pairs)}')
    else:
        data = '<|im_end|>'
    ret = f"data: {data}\n\n"
    print(f'返回qa_pairs响应: {ret}')
    return Response(ret, mimetype="text/event-stream")

def run(**kwargs):
    # from gevent import pywsgi
    # from geventwebsocket.handler import WebSocketHandler
    # server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    # server.serve_forever()
    
    work_dir = kwargs.get('work_dir', os.getcwd())
    here = os.path.dirname(os.path.abspath(__file__))
    # os.chdir(here)

    host = kwargs.get('host', '127.0.0.1')
    port = kwargs.get('port', 5000)
    debug = kwargs.get('debug', False)
    app.run(host=host, port=port, debug=debug)

    os.chdir(work_dir)

if __name__ == "__main__":
    run(debug=True)
    






