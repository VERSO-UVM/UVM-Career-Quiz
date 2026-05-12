from flask import Flask, render_template,request, jsonify
import json

app = Flask(__name__)


# TODO change the route here from "/" to "/quiz builder" whenever we have a real landing page, right now it only exist as a way to actually test the flask 
@app.route('/', methods=['GET', 'POST'])
def quiz_builder():
    if request.method == 'POST':
        print('worked')
    return render_template("quiz_builder.html")



# TODO change the test.json name to something that is unique (and would be unique to each file)
@app.route('/save-quiz', methods=['POST'])
def save_quiz():
    quiz = request.get_json()  
    with open('testing_quiz/test.json', 'w') as f:
        json.dump(quiz, f, indent=2)

    return jsonify({ 'status': 'ok', 'message': 'Quiz saved' })