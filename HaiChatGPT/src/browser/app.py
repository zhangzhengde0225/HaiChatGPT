import os
import time
import openai
import logging
import damei as dm
from flask import Flask, redirect, render_template, request, url_for, Response
from .web_object import WebObject

os.environ['LOGGING_LEVEL'] = str(logging.DEBUG)
logger = dm.get_logger('app')

app = Flask(__name__)
webo = WebObject()


@app.route('/stream')
def stream():
    def generate():
        for i in range(10):
            yield "data: {}\n\n".format(i)
            time.sleep(0.2)
    return Response(generate(), mimetype="text/event-stream")

@app.route("/", methods=("GET", "POST"))
def index():
    print(f'req: {request}. method: {request.method}')
    
    if request.method == "POST":
        # animal = request.form["animal"]
        # response = openai.Completion.create(
        #     model="text-davinci-003",
        #     prompt=generate_prompt(animal),
        #     temperature=0.6,
        # )
        # logger.info(response)
        # return redirect(url_for("index", result=response.choices[0].text))
        text = request.form["prompt"]  # this is the query
        if text == '':
            text = '你是谁？'
        print('text: ', text)
        return webo.query(text)
        # return redirect(url_for("index", result=response))

    result = request.args.get("result")
    # result = '你好'
    return render_template("index.html", result=result)
    

def run(**kwargs):
    # from gevent import pywsgi
    # from geventwebsocket.handler import WebSocketHandler
    # server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    # server.serve_forever()
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    run(debug=True)
    






