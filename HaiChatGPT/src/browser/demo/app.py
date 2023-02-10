"""
运行失败
"""


import time
from flask import Flask
from flask_sockets import Sockets

app = Flask(__name__)
sockets = Sockets(app)

# A simple text generator
def text_generator():
    while True:
        yield "This is a message from the text generator.\n"
        time.sleep(1)

# WebSockets route for handling text generator
@sockets.route('/text_stream')
def text_stream(ws):
    for text in text_generator():
        ws.send(text)
    return

# HTML page for displaying the text
@app.route('/')
def index():
    print(f'one request: {request}. method: {request.method}')
    return '''
    <html>
    <head>
        <script>
            var ws = new WebSocket('ws://' + window.location.host + '/text_stream');
            ws.onmessage = function(event) {
                document.getElementById("text").innerHTML += event.data;
            };
        </script>
    </head>
    <body>
        <div id="text"></div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5001), app, handler_class=WebSocketHandler)
    server.serve_forever()
