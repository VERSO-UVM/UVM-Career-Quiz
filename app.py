from flask import Flask, render_template,request, session, redirect, url_for, jsonify
from flask_cors import CORS
import uuid
import os
import json
import time
import database_interaction as db 
import log_in
import response_table_interaction as ri
import subprocess
from flask_mailing import Mail, Message


app = Flask(__name__)
#TODO this is for testing purpose and will need to be changed as soon as we get a server
app.secret_key = "flask_is_making_me_do_this"

# This allows JS frontend to talk to this backend without security blocks TBD on weather this is a long term solution.
CORS(app) 

app.config.update(
    MAIL_SERVER="localhost",
    MAIL_PORT=1025,
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=False,
    USE_CREDENTIALS=False,
    MAIL_USERNAME="dev",
    MAIL_PASSWORD="dev",
    MAIL_DEFAULT_SENDER="test@example.com",
    MAIL_FROM_NAME="Quiz App (dev)"
)
mail = Mail(app)

# @app.route('/send-test-email', methods=['POST'])
# async def send_test_email():
#     message = Message(
#         subject="Quiz app notification",
#         recipients=["shadekopf@gmail.com"],
#         body="Hello from the quiz app!",
#         subtype="plain"
#     )
#     await mail.send_message(message)
#     return jsonify({"status": "Email sent"})


@app.route('/send-quiz-email', methods=['POST'])
async def send_quiz_email():
    if not session.get("user_id"):
        return require_login("Please log in first")

    data = request.get_json() or {}
    email = data.get('email', '').strip()
    body = data.get('body', '').strip()
    quiz_id = data.get('quizID', '').strip()

    if not email:
        return jsonify({"error": "missing email address"}), 400

    message = Message(
        subject="Your quiz results",
        recipients=[email],
        body = body,
        subtype= "plain"
    )

    try:
        await mail.send_message(message)
    except Exception as e:
        print(f"Failed to send quiz email: {e}")
        return jsonify({"error": "Failed to send email"}), 500

    return jsonify({"success": "Email sent"}), 200


def get_role(quiz_id: str) -> str:
    """
    Get the role of the current logged-in user for a specific quiz. Mainly a wrapper for the db function of the same name.

    Args:
        quiz_id: the id of the quiz to get the role for

    Returns:
        str : the role of the user
    """
    return str(db.get_role(session["user_id"], quiz_id))

@app.route('/get-user-id', methods=['GET'])
def get_user_id():
    """
    Return the current logged-in user's id as a JSON response.
    Intended to allow the frontend to retrieve the session user id without
    exposing the full session object.

    Returns:
        200: JSON object containing the user's id if the user is logged in
        404: if no user_id is found in the session (user is not logged in)
    """
    if "user_id" in session:
        return jsonify({"userId": session["user_id"]})
    return jsonify({"error": "Not logged in"}), 404


@app.route("/")
def login_page():
    """
    Render the welcome page where the user can choose to log in or register.
    """
    return render_template("login_page.html")

@app.route("/logout")
def logout():
    """
    Log the current user out by clearing their session data and render the logged out confirmation page.

    Returns:
        200: the logged_out.html page confirming the user has been logged out
    """
    session['user_id'] = None
    session['username'] = None
    session['email'] = None
    return render_template("logged_out.html")


@app.route("/quiz_login", methods=['GET', 'POST'])
def quiz_login():
    """
    Render the login page and handle login form submissions.
    On POST, validates the provided credentials and logs the user in.
    On GET, renders the login form.

    Returns:
        GET  200: the quiz_login.html page
        POST 200: the quiz_login.html page with an error message on failure
        POST 302: redirect to quiz_selection on success
    """
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



@app.route("/register",methods=['GET', 'POST'])
def register():
    """
    Render the registration page and handle registration form submissions.
    On GET, renders the registration form.
    On POST, attempts to register the user and logs them in on success, redirecting them to quiz_selection.

    Returns:
        GET  200: the register.html page
        POST 200: the register.html page with an error message on failure
        POST 302: redirect to quiz_selection on success
    """
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
#TODO: there are 2 versions of require login not sure which one actually works
def require_login(reason=None):
    """
    Render the access denied page when a user tries to access certain page without being logged in.

    Args:
        reason: optional message explaining why access was denied

    Returns:
        403: the access_denied.html page with the reason message
    """
    return render_template("access_denied.html", reason=reason), 403

@app.route("/quiz_builder/<quiz>", methods=["GET", "POST"])
def quiz_builder(quiz):
    """
    Render the quiz builder page for a given quiz id.
    If the quiz does not exist yet (new quiz), grants the user creator role.
    If the quiz exists but the user has no access to it, redirects to quiz_selection.
    Loads the quiz data from the corresponding JSON file if it exists.

    Args:
        quiz: the id of the quiz to build, or 'new_quiz' for a new one (done in quiz_selection.html)

    Returns:
        200: the quiz_builder.html page with the quiz data and user role
        302: redirect to quiz_selection if the user has no access
        403: access_denied.html if the user is not logged in
    """
    if not session.get("user_id"):
        return require_login("You need to log in to access the quiz builder.")
    
    # Handle a new_quiz explicitly
    if quiz == "new_quiz":
        role = db.ROLE_CREATOR
        quiz_ = {"title": "", "desc": "", "id": "new_quiz", "categories": []}
        return render_template("quiz_builder.html", quiz=quiz_, user_role=role)

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
        pass

    return render_template("quiz_builder.html", quiz=quiz_, user_role=role)



@app.route('/save_quiz', methods=['POST'])
def save_quiz():
    """
    Save the quiz JSON sent from the frontend to the server.

    Returns:
        200: JSON with the quiz id and last_modified timestamp on success
        200: JSON with an error message if the user lacks edit permission
        409: JSON with an error message if the quiz was modified concurrently
        403: access_denied.html if the user is not logged in
    """
    if session["user_id"]:
        quiz = request.get_json()

        # Check if it's a brand new quiz
        is_new = (quiz.get("id") == "new_quiz" or not quiz.get("id"))

        # Generate the unique ID if it's new
        if is_new:
            quiz["id"] = str(uuid.uuid4())
        
        # Only enforce permission checks on existing quizzes
        if not is_new:
            role = get_role(quiz["id"])
            if role and not db.can_edit(role):
                return jsonify({"error" : "You do not have the permission to edit this quiz"}), 403
        
        # Save the file layout
        path = f'testing_quiz/{quiz["id"]}.json'
        if os.path.exists(path):
            with open(path) as f:
                saved = json.load(f)
            if saved.get('last_modified') != quiz.get('last_modified'):
                return jsonify({"error": "This quiz was modified by someone else. Please refresh and redo your changes."}), 409

        quiz['last_modified'] = time.time()
        with open(path, 'w') as f:
            json.dump(quiz, f, indent=2)

        # Save to database 
        db.save_quiz_in_the_db(quiz["id"], quiz["title"], session["user_id"])
        
        return jsonify({"success": True, "id": quiz["id"], "last_modified": quiz["last_modified"]})
    
    return require_login("You need to log in to save a quiz.")



#Allow the user to choose a quiz from our server, and upon choosing send them to quiz_builder. The two list are kind of a bruteforce strategy, but it should work (or at least it has so far)
@app.route("/quiz_selection", methods=['GET', 'POST'])
def quiz_selection():
    """
    Render the quiz selection page, listing all quizzes the current user has access to.

    Returns:
        200: the quiz_selection.html page with the list of accessible quizzes
        403: access_denied.html if the user is not logged in
    """
    if session["user_id"]:
        folder_path = './testing_quiz'
        quiz = []
        name =[]
        for filename in os.listdir(folder_path):
            if(db.has_access(session['user_id'], filename[:-5])):
                quiz.append(filename[:-5])
        for q in quiz:
            name.append(db.find_name_with_id(q))
        return render_template("quiz_selection.html", quizzes = quiz, names = name, count = 0, username = session["username"])
    return require_login("You need to log in to see your quizzes.")

@app.route("/quiz_preview/<quiz>")
def quiz_preview(quiz):
    """
    Render the quiz preview page for a given quiz id.

    Args:
        quiz: the id of the quiz to preview

    Returns:
        200: the quiz_preview.html page with the quiz data
        302: redirect to quiz_selection if the user has no access to the quiz
        403: access_denied.html if the user is not logged in
    """
    if session["user_id"]:
        role = get_role(quiz)
        if role:
            with open(f'testing_quiz/{quiz}.json') as f:
                quiz_ = json.load(f)
            return render_template("quiz_preview.html", quiz = quiz_)
        else:
            redirect("/quiz_selection")
    return require_login("You need to log in to preview a quiz.")

#TODO: this is currently not working as intended, the library for fetching quiz info is changed WIP
@app.route("/available_quizzes", methods=['GET','POST'])
def show_available_quizzes():
    """
    Render the available quizzes page.

    Returns:
        200: the available_quizzes.html page with assigned and completed quiz lists
        403: access_denied.html if the user is not logged in
    """
    if session["user_id"]:
        #TODO: db.quizzes for user is legacy, new system is intending to use the response table interaction one, not sure how this will affect other functionality
        # I'm tracking it right now but it seems like this is highly embedded, a jank solution may be required until everything can be updated accordingly
        assigned_quizzes = db.quizzes_for_user(session["user_id"])
        completed_quizzes = []    
        _, completed = ri.lookup_user_todo_completed_quizzes(session['user_id']) # idk anymore- wip seems to have to do with a case where completed has to have __iter__ but is None
        completed_quizzes = [
                {"id": q, "name": db.find_name_with_id(q)}
                for q in completed ]
        
        completed_quizzes = []

        return render_template("available_quizzes.html", assigned_quizzes=assigned_quizzes, completed_quizzes=completed_quizzes)
    return require_login("You need to log in see the quizzes available to you.")
"""
this is a possible fix
@app.route("/available_quizzes", methods = ['GET', 'POST'] 
def show_available_quizzes():
    if session["user_id"]
    assigned, completed = ri.lookup_user_todo_completed_quizzes(session['user_id'])
    
"""

@app.route("/quiz_share", methods=['GET','POST'])
def quiz_share():
    """
    Handle sharing a quiz with another user.
    On GET, returns a JSON list of users who currently have access to the quiz, along with the current user's sharing permissions.
    On POST, shares the quiz with the specified user at the specified role, subject to permission checks.

    Returns:
        GET  200: JSON with the list of users, their roles, and sharing permissions
        POST 200: JSON success message on successful share
        POST 200: JSON error message if permissions are insufficient or user not found
        403: access_denied.html if the user is not logged in
    """
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
    return require_login("You need to log in to share a quiz.")



@app.route('/assign_quiz', methods=['POST'])
def assign_quiz():
    """
    Assign a quiz to a user by giving them reader access to it.
    Only users with share permissions (creator or admin) can assign quizzes.

    Returns:
        200: JSON success message if the quiz was assigned successfully
        200: JSON error message if the user does not exist or already has access
        403: JSON error message if the current user lacks share permission
        403: access_denied.html if the user is not logged in
    """
    if session.get('user_id'):
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        quiz_id = data.get('quiz_id', '').strip()

        if not username or not quiz_id:
            return jsonify({"error": "Missing username or quiz id."})

        u_role = get_role(quiz_id)
        if not db.can_share(u_role):
            return jsonify({"error": "You do not have permission to assign this quiz."}),403

        target_id = db.find_id_with_uname(username)
        if not target_id:
            return jsonify({"error": "This user does not exist"})

        if db.has_access(target_id, quiz_id):
            return jsonify({"error": "This user already has access to this quiz"})

        # Assign as reader so the user can take the quiz
        db.share_quiz(target_id, quiz_id, db.ROLE_READER)
        return jsonify({"success": f"Quiz assigned to {username}."})
    return require_login("You need to log in to assign a quiz.")

#TODO: same type problem as quiz revoke wip
@app.route("/quiz_update_role", methods=["POST"])
def quiz_update_role():
    """
    Update the role of a user for a specific quiz.
    The current user must have share permissions and cannot assign a role equal to or higher than their own.

    Returns: 
        200: JSON success message if the role was updated successfully
        200: JSON error message if permissions are insufficient or the role is invalid
        403: access_denied.html if the user is not logged in
    """
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
    return require_login("You need to log in to update the role of a user.")
#TODO: this is throwing some type nonsense, I am following the path to see where it can be fixed - ej 7/9/26 
@app.route('/quiz_revoke', methods=['POST'])
def quiz_revoke():
    """
    Revoke a user's access to a quiz.
    Only creators and admins can revoke access, and the creator's own access
    cannot be revoked.
    TODO may want to add a way for the creator to transfer ownership to someone else.
    Returns:
        200: JSON success message if access was revoked successfully
        200: JSON error message if permissions are insufficient or the target is the creator
        403: access_denied.html if the user is not logged in
    """
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
    return require_login("You need to log in to revoke a user's access to a quiz.")

@app.route('/go_back')
def go_back():
    """
    Redirect the user to their previous page if stored in the session,
    falling back to quiz_selection if no previous page is recorded.

    Returns:
        302: redirect to the previous page or quiz_selection
    """
    prev = session.get('previous_page')
    if prev:
        return redirect(prev)
    return redirect("/quiz_selection")

@app.route("/quiz_delete", methods =['POST'])
def quiz_delete():
    """
    Delete a quiz entirely, removing it from both the database and the filesystem.
    Only the creator of the quiz can delete it.

    Returns:
        200: JSON with a redirect URL to quiz_selection on success
        200: JSON error message if the current user is not the creator
        200: JSON error message if the deletion failed unexpectedly
        403: access_denied.html if the user is not logged in
    """
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
    return require_login("You need to log in to delete a quiz.")


#TODO: this is probably the wrong require login so it is commented out for now
"""
def require_login(reason=None):
    return render_template("access_denied.html", reason=reason)
"""

# Accepts the post request from flask that contains a users completed quiz data package
# Then sends it to be processed into the database
#TODO: WARNING!!!!
# this will need significant encryption and other protections most likely, i would look into either an rsa or other encryption algorithm, 
#this data needs circuit compression style algorithms and those cannot be done on encrypted data, so we should make sure that any data 
#that gets sent to rti.py gets decrypted for joined on the table
# the result if not could be un-recoverable 
@app.route('/quiz-data', methods=['POST'])
def receive_user_quiz_data():

    data = request.get_json()
    nice_json_string = json.dumps(data, indent=2)

    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    # runs command to execute the test file
    result = subprocess.run(
            ['python3', 'test_posted_user_data.py', nice_json_string], 
            capture_output=True, 
            text=True            
        )
    
    print("--- Test Script Output ---")
    print(result.stdout) 
    print("----------------------------")

    return jsonify({
        "status": "success",
    }), 200
