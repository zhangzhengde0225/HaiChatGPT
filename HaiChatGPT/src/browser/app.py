import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

import damei as dm

logger = dm.get_logger('app')


class X(object):
    def __init__(self) -> None:
        self.count = 0

    def query(self, text):
        self.count += 1
        return f'I am the anser {self.count}.'

xx = X()

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
        prompt = request.form["prompt"]
        logger.info(prompt)
        response = xx.query(prompt)
        return redirect(url_for("index", result=response))


    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(animal):
    return """Suggest three names for an animal that is a superhero.

Animal: Cat
Names: Captain Sharpclaw, Agent Fluffball, The Incredible Feline
Animal: Dog
Names: Ruff the Protector, Wonder Canine, Sir Barks-a-Lot
Animal: {}
Names:""".format(
        animal.capitalize()
    )






