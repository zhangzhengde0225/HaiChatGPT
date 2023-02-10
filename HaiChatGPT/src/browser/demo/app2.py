"""
这个可以运行！
"""

from flask import Flask, Response
import time

app = Flask(__name__)

@app.route('/stream')
def stream():
    def generate():
        for i in range(10):
            yield "data: {}\n\n".format(i)
            time.sleep(1)
    return Response(generate(), mimetype="text/event-stream")

@app.route('/')
def index():
    return """
        <html>
            <head>
                <script>
                    var source = new EventSource("/stream");
                    source.onmessage = function(event) {
                        document.getElementById("output").innerHTML += event.data + "<br>";
                    };
                </script>
            </head>
            <body>
                <h1>Server-Sent Events Example</h1>
                <div id="output"></div>
            </body>
        </html>
    """

if __name__ == '__main__':
    app.run(port=5002)
