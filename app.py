from flask import Flask, render_template,request, session, redirect, url_for
import os
import json
import db_creation_and_experiment as db 
import log_in

app = Flask(__name__)
#TODO this is for testing purpose and will need to be changed as soon as we get a server
app.secret_key = "flask_is_making_me_do_this"

@app.route("/")
def login_page():
    session['user_id'] = None
    session['username'] = None 
    return render_template("login_page.html")

@app.route("/quiz_login", methods=['GET', 'POST'])
def quiz_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        result = log_in.login_customer(username, password)
        if result == -1:
            return render_template('quiz_login.html', error="This username does not exist.")
        if result == -2:
            return render_template('quiz_login.html', error="The password provided is not the correct one.")
        else:
            session['user_id'] = result
            session['username'] = username 
            return redirect(url_for('quiz_selection'))
    return render_template("quiz_login.html")

@app.route("/register")
def register():
    return render_template("register.html")



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
        db.save_quiz_in_the_db(quiz["id"], quiz["title"],session['user_id'])
    return render_template('quiz_builder.html', quiz=quiz)


@app.route("/quiz_selection", methods=['GET', 'POST'])
def quiz_selection():
    folder_path = './testing_quiz'
    quiz = []
    name =[]
    for filename in os.listdir(folder_path):
        if(db.has_acess(session['user_id'], filename[:-5])):
            quiz.append(filename)
    for q in quiz:
        name.append(db.find_name_with_id(q[:-5]))
    return render_template("quiz_selection.html", quizzes = quiz, names = name, count = 0)
