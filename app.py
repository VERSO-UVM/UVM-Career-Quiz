from flask import Flask, render_template,request, session, redirect, url_for, jsonify
import uuid
import os
import json
import database_interaction as db 
import log_in


app = Flask(__name__)
#TODO this is for testing purpose and will need to be changed as soon as we get a server
app.secret_key = "flask_is_making_me_do_this"
#TODO / CONCERN do we need to have a banner regarding privacy policy?



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
@app.route('/quiz_builder/<quiz>', methods=['GET', 'POST'])
def quiz_builder(quiz):
    if session['user_id'] :
        quiz_ = {"title": "", "desc": "", "id": "", "categories": []}
        try:
            with open(f'testing_quiz/{quiz}.json') as f:
                quiz_ = json.load(f)
            if db.has_acess(session["user_id"],quiz):
                quiz_ = quiz_ 
            else : 
                quiz_ = {"title": "", "desc": "", "id": "", "categories": []}
        except FileNotFoundError as e:
            error = "So far this is just a way to bypass the problem of creating new quiz."
        return render_template('quiz_builder.html', quiz =quiz_)
    else :
        return redirect("/")


#Button on the quiz builder page, allow a user to save a quiz in our server. As it stand there is no option to delete the quiz. We will need to work on that
@app.route('/save_quiz', methods=['GET','POST'])
def save_quiz():
    quiz = request.get_json()
    if(not quiz["id"]):
        quiz["id"] = str(uuid.uuid4())
    with open(f'testing_quiz/{quiz["id"]}.json', 'w') as f:
        json.dump(quiz, f, indent=2)
        db.save_quiz_in_the_db(quiz["id"], quiz["title"],session['user_id'])
    return jsonify({"redirect": url_for('quiz_builder', quiz=quiz["id"])})


@app.route('/drawflow_testing')
def drawflow_testing():
    return render_template('drawflow_testing.html')




#Allow the user to choose a quiz from our server, and upon choosing send them to quiz_builder. The two list are kind of a bruteforce strategy, but it should work (or at least it has so far)
@app.route("/quiz_selection", methods=['GET', 'POST'])
def quiz_selection():
    if session["user_id"]:
        folder_path = './testing_quiz'
        quiz = []
        name =[]
        for filename in os.listdir(folder_path):
            if(db.has_acess(session['user_id'], filename[:-5])):
                quiz.append(filename[:-5])
        for q in quiz:
            name.append(db.find_name_with_id(q))
        return render_template("quiz_selection.html", quizzes = quiz, names = name, count = 0)
    else : 
        return redirect("/")

@app.route("/quiz_preview/<quiz>")
def quiz_preview(quiz):
    if session["user_id"]:
        with open(f'testing_quiz/{quiz}.json') as f:
            quiz_ = json.load(f)
        return render_template("quiz_preview.html", quiz = quiz_)
    else : 
        return redirect("/")


@app.route("/quiz_share", methods=['GET','POST'])
def quiz_share():
    if session["user_id"]:
        if request.method == 'GET':
            users_ = []
            quiz_id = request.args.get('quiz_id', '').strip()
            users = db.user_with_acess(quiz_id)
            creator = db.find_creator(quiz_id)
            if users:
                for u in users:
                    users_.append(db.find_uname_with_id(u[0]))
            return jsonify({
                "users": users_,
                "creator": creator,
                "current_user": session['username']
            })
    
        error =""
        data = request.get_json()
        username = data.get('username', '').strip()
        quiz_id = data.get('quiz_id', '').strip()

        u_id = db.find_id_with_uname(username)

        if(u_id ):
            if u_id == session['user_id']:
               error = "This is you..."
            elif(not db.has_acess(u_id, quiz_id)):
                db.share_quiz(u_id, quiz_id)
            else:
                error = "This user already has acces to this quiz"
        else:
            error = "This user does not exist"

        if error:
            return jsonify({"error": f"A problem occured when trying to share your quiz! <br> {error}."})
        return jsonify({"success": f"Quiz successfully shared with {username}!"})
    else: 
        return redirect("/")

@app.route('/quiz_revoke', methods=['POST'])
def quiz_revoke():
    data = request.get_json()
    username = data.get('username', '').strip()
    quiz_id = data.get('quiz_id', '').strip()

    if session['username'] != db.find_creator(quiz_id):
        return jsonify({"error": "Only the creator can remove access."})

    u_id = db.find_id_with_uname(username)


    db.remove_access(u_id, quiz_id)
    return jsonify({"success": f"Access removed for {username}."})


@app.route("/quiz_delete", methods =['POST'])
def quiz_delete():
    data = request.get_json()
    quiz_id = data.get('quiz_id', ''.strip())

    if session['username'] != db.find_creator(quiz_id):
        return jsonify({"error" : "Only the creator, and people with the allowed permision, can delete a quiz."})
    
    db.delete_quiz()
    return jsonify({"sucess" : "Your quiz has been deleted."})
