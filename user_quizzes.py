import response_table_interaction as ri

def fetch_curr_user(username: str, verified: bool):
    return ri.lookup_user_todo_completed_quizzes(username)
        #on available quizzes.html display all quizzes 2 sections, user completed vs not 
    

def display_user_quizzes():
    pass

def display_completed_quizzes():
    pass
        
def assign_quiz_to_user(username, quiz_id):
    pass
def remove_quiz_from_user():
    pass

def load_curr_quiz(quiz_id):
    """fetch json of current quiz, send to html page for display"""

