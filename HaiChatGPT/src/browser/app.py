import os

import openai
import logging
import damei as dm
from flask import Flask, redirect, render_template, request, url_for
from .web_object import WebObject

app = Flask(__name__)
os.environ['LOGGING_LEVEL'] = str(logging.DEBUG)
logger = dm.get_logger('app')

wo = WebObject()

@app.route("/", methods=("GET", "POST"))
def index():
    print(request)
    
    if request.method == "POST":
        # animal = request.form["animal"]
        # response = openai.Completion.create(
        #     model="text-davinci-003",
        #     prompt=generate_prompt(animal),
        #     temperature=0.6,
        # )
        # logger.info(response)
        # return redirect(url_for("index", result=response.choices[0].text))
        request = request.form["prompt"]  # this is the query
        # logger.debug(f'prompt: {request}')
        # response = chatgpt.query(prompt)
        wo.query(request)
        # logger.debug(f'response: {response}')
        # return redirect(url_for("index", result=response))


    result = request.args.get("result")
    return render_template("index.html", result=result)
    

def run(**kwargs):
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    run(debug=True)
    






