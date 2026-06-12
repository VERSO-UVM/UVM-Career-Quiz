from flask import Flask, render_template,request, session, redirect, url_for, jsonify
import uuid
import os
import json
import time
import database_interaction as db 
import log_in


app = Flask(__name__)
#TODO this is for testing purpose and will need to be changed as soon as we get a server
app.secret_key = "flask_is_making_me_do_this"


def get_role(quiz_id):
    return db.get_role(session["user_id"], quiz_id)

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
@app.route("/quiz_builder/<quiz>", methods=["GET", "POST"])
def quiz_builder(quiz):
    if not session["username"]:
        return redirect("/")
 
    role = get_role(quiz)
 
    if not role:
        
        if os.path.exists(f"testing_quiz/{quiz}.json"):
            return redirect(url_for("quiz_selection"))
        role = db.ROLE_CREATOR
 
    quiz_ = {"title": "", "desc": "", "id": quiz, "categories": []}
    try:
        with open(f"testing_quiz/{quiz}.json") as f:
            quiz_ = json.load(f)
    except FileNotFoundError:
         error = "So far this is just a way to bypass the problem of creating new quiz." 
 
    return render_template("quiz_builder.html", quiz=quiz_, user_role=role)

#Button on the quiz builder page, allow a user to save a quiz in our server.
@app.route('/save_quiz', methods=['POST'])
def save_quiz():
    if session["user_id"]:

        quiz = request.get_json()

        if quiz["id"] == "new_quiz" or not quiz["id"]:
            quiz["id"] = str(uuid.uuid4())

        
        if get_role(quiz["id"]) and not db.can_edit(get_role(quiz["id"])):
            return jsonify({"error" : "You do not have the permision to edit this quiz"}) 
        
        path = f'testing_quiz/{quiz["id"]}.json'

        if os.path.exists(path):
            with open(path) as f:
                saved = json.load(f)
            if saved.get('last_modified') != quiz.get('last_modified'):
                return jsonify({"error": "This quiz was modified by someone else. Please refresh and redo your changes."})


        quiz['last_modified'] = time.time()
        with open(path, 'w') as f:
            json.dump(quiz, f, indent=2)

        db.save_quiz_in_the_db(quiz["id"], quiz["title"], session["user_id"])
        return jsonify({"success": True, "id": quiz["id"]})
    
    return redirect("/")



#Allow the user to choose a quiz from our server, and upon choosing send them to quiz_builder. The two list are kind of a bruteforce strategy, but it should work (or at least it has so far)
@app.route("/quiz_selection", methods=['GET', 'POST'])
def quiz_selection():
    if session["user_id"]:
        folder_path = './testing_quiz'
        quiz = []
        name =[]
        for filename in os.listdir(folder_path):
            if(db.has_access(session['user_id'], filename[:-5])):
                quiz.append(filename[:-5])
        for q in quiz:
            name.append(db.find_name_with_id(q))
        return render_template("quiz_selection.html", quizzes = quiz, names = name, count = 0)
    else : 
        return redirect("/")

@app.route("/quiz_preview/<quiz>")
def quiz_preview(quiz):
    if session["user_id"]:
        role = get_role(quiz)
        if role:
            with open(f'testing_quiz/{quiz}.json') as f:
                quiz_ = json.load(f)
            return render_template("quiz_preview.html", quiz = quiz_)
        else:
            redirect("/quiz_selection")
    else : 
        return redirect("/")


@app.route("/quiz_share", methods=['GET','POST'])
def quiz_share():
    if session["user_id"]:
        if request.method == 'GET':
            quiz_id = request.args.get("quiz_id", "").strip()
            u_role = get_role(quiz_id)
            raw = db.user_with_access(quiz_id) or []
            users_list = []
            for row in raw:
                username = db.find_uname_with_id(row[0])
                role = row[2] if len(row) > 1 else db.ROLE_READER
                users_list.append({
                    "username": username,
                    "role": role,
                    "can_revoke": (
                        db.can_revoke(u_role)
                        and role != db.ROLE_CREATOR
                        and username != session["username"]
                    )
                })
            return jsonify({
                "users": users_list,
                "actor_role": u_role,
                "can_share": db.can_share(u_role),
                "current_user": session["username"]
                })
    
        error =""
        data = request.get_json()
        username = data.get('username', '').strip()
        quiz_id = data.get('quiz_id', '').strip()
        new_role   = data.get("role", db.ROLE_READER)
 
        u_role = get_role(quiz_id)
        if not db.can_share(u_role):
            return jsonify({"error": "You do not have permission to share this quiz."})
 
        
        if not db.can_promote(u_role, new_role):
            return jsonify({"error": f"You cannot assign the '{new_role}' role."})
 
        u_id = db.find_id_with_uname(username)

        if(u_id ):
            if u_id == session['user_id']:
               error = "This is you..."
            elif(not db.has_access(u_id, quiz_id)):
                db.share_quiz(u_id, quiz_id, new_role)
            else:
                error = "This user already has acces to this quiz"
        else:
            error = "This user does not exist"

        if error:
            return jsonify({"error": f"A problem occured when trying to share your quiz! <br> {error}."})
        return jsonify({"success": f"Quiz successfully shared with {username}!"})
    else: 
        return redirect("/")


@app.route("/quiz_update_role", methods=["POST"])
def quiz_update_role():
    if session["username"]:
 
        data     = request.get_json()
        username = data.get("username", "").strip()
        quiz_id  = data.get("quiz_id",  "").strip()
        new_role = data.get("role",     "").strip()
    
        u_role = get_role(quiz_id)
        if not db.can_share(u_role):
            return jsonify({"error": "You do not have permission to change roles."})
    
        target_id   = db.find_id_with_uname(username)
        target_role = db.get_role(target_id, quiz_id)
    
        
        if target_role == db.ROLE_CREATOR:
            return jsonify({"error": "The creator's role cannot be changed."})
    
        if not db.can_promote(u_role, new_role):
            return jsonify({"error": f"You cannot assign the '{new_role}' role. As it is higher or similar to your own rank"})
    
        try:
            db.update_role(target_id, quiz_id, new_role)
        except ValueError as e:
            return jsonify({"error": str(e)})
    
        return jsonify({"success": f"Role updated to {new_role} for {username}."})
    redirect("/")

@app.route('/quiz_revoke', methods=['POST'])
def quiz_revoke():
    if session["username"]:
        data = request.get_json()
        username = data.get('username', '').strip()
        quiz_id = data.get('quiz_id', '').strip()

        u_role = get_role(quiz_id)
        if not db.can_revoke(u_role):
            return jsonify({"error": "Only creators and admins can remove access."})
        
        target_id   = db.find_id_with_uname(username)
        target_role = db.get_role(target_id, quiz_id)
        
        if target_role == db.ROLE_CREATOR:
            return jsonify({"error": "The creator's access cannot be revoked."})
        
        db.remove_access(target_id, quiz_id)
        return jsonify({"success": f"Access removed for {username}."})
    return redirect("/")


@app.route("/quiz_delete", methods =['POST'])
def quiz_delete():
    if session["username"]:
        data = request.get_json()
        quiz_id = data.get('quiz_id', ''.strip())

        if session['username'] != db.find_creator(quiz_id):
            return jsonify({"error" : "Only the creator can delete the quiz."})
        
        worked = db.delete_quiz(quiz_id)
        if worked:
            path = f"testing_quiz/{quiz_id}.json"
            os.remove(path)
            return jsonify({"redirect": url_for('quiz_selection')})
        else: 
            return jsonify({"error" : "A problem happened while trying to delete your quiz"})
    redirect("/")
