import sqlite3
quizzes_to_be_done = []
complete_quizzes = []
class Quiz:
    is_complete : bool = False
    quiz_id : str = ""

    def __init__(self, quiz_id : str):
        self.is_complete = False
        self.quiz_id = quiz_id
    
    def get_quiz_id(self):
        return self.quiz_id
    def complete_quiz(self):
        self.is_complete =True
    def is_completed(self):
        return self.is_complete

def fetch_curr_user(username: str, verified: bool):
        """sql query to fetch user data once logged in"""
        query_result = ["sdfduhg", "forth", "23jfrd"]
        data = [Quiz(quiz_id) for quiz_id in query_result]
        if verified:
            user_quizzes = data
            for quiz in user_quizzes:
                if not quiz.is_completed():
                    quizzes_to_be_done.append(quiz)
                else:
                    complete_quizzes.append(quiz)
            """sql query update user quizzes in categories"""
            return (quizzes_to_be_done, complete_quizzes)
        
        else:
            return("Unable to access user quizzes")
        #on available quizzes.html display all quizzes 2 sections, user completed vs not 
    

def display_user_quizzes():
    pass

def display_completed_quizzes():
    pass
        
def assign_quiz_to_user(username, quiz_id):
    """sql query fetch user"""
    username = ""
    pass

def remove_quiz_from_user():
    pass

def load_curr_quiz(quiz_id):
    """fetch json of current quiz, send to html page for display"""

