from flask import Flask, render_template,request
import os
import json
import db_creation_and_experiment as db 

app = Flask(__name__)


@app.route('/quiz_builder/<quiz>', methods=['GET', 'POST'])
def quiz_builder(quiz):
    quiz_ = {"title": "", "desc": "", "id": "", "categories": []}
    error = ""
    try:
        with open(f'testing_quiz/{quiz}') as f:
            quiz_ = json.load(f)
    except FileNotFoundError as e:
        error = e 
    return render_template('quiz_builder.html', quiz =quiz_, error = error)



@app.route('/save-quiz', methods=['POST'])
def save_quiz():
    quiz = request.get_json()
    with open(f'testing_quiz/{quiz["id"]}.json', 'w') as f:
        json.dump(quiz, f, indent=2)
        db.save_quiz_in_the_db(quiz["id"], quiz["title"])
    return render_template('quiz_builder.html', quiz=quiz)


# TODO this is good if we think the user is in a "single-player" state. We need to refactor this to have some more verification, but for now it will have to do. 
@app.route("/", methods=['GET', 'POST'])
def quiz_selection():
    folder_path = './testing_quiz'
    quiz = []
    name =[]
    for filename in os.listdir(folder_path):
        quiz.append(filename)
    for q in quiz:
        name.append(db.find_name_with_id(q[:-5]))
    return render_template("quiz_selection.html", quizzes = quiz, names = name, count = 0)