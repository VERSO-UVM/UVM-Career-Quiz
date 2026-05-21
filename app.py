from flask import Flask, render_template,request, session, redirect, url_for
import os
import json
import database_interaction as db 
import log_in


app = Flask(__name__)
#TODO this is for testing purpose and will need to be changed as soon as we get a server
app.secret_key = "flask_is_making_me_do_this"



#Simple page, allow the user to choose between login in and registering. Set all session item to none in order to "Reset" the user and log them out
@app.route("/")
def login_page():
    session['user_id'] = None
    session['username'] = None 
    session['email'] = None
    return render_template("login_page.html")


#Log in a user, call functions from the log_in file. 
#Might want to implement the option to log in with email at one point
@app.route("/quiz_login", methods=['GET', 'POST'])
def quiz_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        result = log_in.login_user(username, password)
        if result == -1:
            return render_template('quiz_login.html', error="This username does not exist.")
        if result == -2:
            return render_template('quiz_login.html', error="The password provided is not the correct one.")
        else:
            session['user_id'] = result
            session['username'] = username 
            return redirect(url_for('quiz_selection'))
    return render_template("quiz_login.html")


#Register a user into the database
@app.route("/register",methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        new_id = log_in.registering_user(username, password, email)
        if new_id == -1:
            return render_template('register.html', error="Username already exists, please choose another.")
        if new_id == -2:
            return render_template('register.html', error="This email is already in use please log in to that account.")
        session['user_id'] = new_id
        session['username'] = username 
        return redirect(url_for('quiz_selection'))
    return render_template("register.html")



# Allow the user to create and make modification to quizzes.
#As it stand the cooperative aspect is a bit forlorn, will need to add option for sharing for example.
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


#Button on the quiz builder page, allow a user to save a quiz in our server. As it stand there is no option to delete the quiz. We will need to work on that
@app.route('/save-quiz', methods=['POST'])
def save_quiz():
    quiz = request.get_json()
    with open(f'testing_quiz/{quiz["id"]}.json', 'w') as f:
        json.dump(quiz, f, indent=2)
        db.save_quiz_in_the_db(quiz["id"], quiz["title"],session['user_id'])
    return render_template('quiz_builder.html', quiz=quiz)


@app.route('/drawflow_testing')
def drawflow_testing():
    return render_template('drawflow_testing.html')




#Allo the user to choose a quiz from our server, and upon choosing send them to quiz_builder. The two list are kind of a bruteforce strategy, but it should work (or at least it has so far)
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

@app.route("/quiz_preview/<quiz>")
def quiz_preview(quiz):
    with open(f'testing_quiz/{quiz}.json') as f:
        quiz_ = json.load(f)
    return render_template("quiz_preview.html", quiz = quiz_)