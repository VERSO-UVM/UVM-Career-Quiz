from flask import Flask, render_template,request, jsonify
import json

app = Flask(__name__)


# TODO change the route here from "/" to "/quiz builder" whenever we have a real landing page, right now it only exist as a way to actually test the flask 
# TODO right now it only accept "testing_quiz/pjo4roy.json" as an argument, once we have quiz_selection done, we would wnat it to pass the name of the file to this, and open the file this way
@app.route('/', methods=['GET', 'POST'])
def quiz_builder():
    quiz = {"title": "", "desc": "", "id": "", "categories": []}
    error = ""
    try:
        with open('testing_quiz/testing_quiz/pjo4roy.json') as f:
            quiz = json.load(f)
    except FileNotFoundError as e:
        error = e 
    return render_template('quiz_builder.html', quiz=quiz, error = error)



# TODO change the test.json name to something that is unique (and would be unique to each file)
@app.route('/save-quiz', methods=['POST'])
def save_quiz():
    quiz = request.get_json()
    with open(f'testing_quiz/{quiz["id"]}.json', 'w') as f:
        json.dump(quiz, f, indent=2)
    return render_template('quiz_builder.html', quiz=quiz)