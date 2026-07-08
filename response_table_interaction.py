import json
import sqlite3
import csv
import pickle
import app
import os 
#TODO: check sql queries to ensure correct data is being handled, make sure that any errors that occur for now cannot happen in prod, a lot of this can be dangerous if serial data can be mixed with unserialzed data and either re-serialized or joined wrong, all data types must be checked in every function. 
#-----------------------------------WARNING!!!!!----------------------------------------------------





# THIS FILE OPERATES ON CORE DATA THAT CANNOT BE DAMAGED IN ANY WAY AND WILL BE DIFFICULT TO RECOVER, ALTERING ANYTHING MUST BE PAIRED WITH TESTING OF ALL END BEHAVIORS OF RESULTING -
# STATE. THIS PROGRAM CAN AND WILL LEAD TO UNINTENDED CONSEQUENSES ACROSS LARGE QUANTITIES OF SENSITIVE USER DATA THAT WILL PROVIDE INACCURATE RESULTS AND SYSTEM LEVEL ERRORS IF -
# FUNCTIONS ARE ALTERED IN A WAY THAT DISRUPTS THE PROCESS THAT ALL FUNCTIONS MUST FOLLOW AS DETAILED BELOW.




#ALL FUNCTIONS MUST BEHAVE IN THIS WAY: RETRIEVE DATA FROM DB IF NECESSARY, RETURN DATA FROM SERIALIZED FORM TO LIST FORM, PERFORM OPERATIONS NECESSARY TO BUSINESS LOGIC, CONSIDER BRANCHING BEHAVIORS AND DO NOT TRACK ANSWERS TO INDIVIDUAL QUIZZES ON A GLOBAL STATE AS THE VARIANCE CREATED THROUGH BRANCHING CAN CAUSE DIFFERENT QUIZ LENGTHS ALONG THE USER SPACE, WHEN DATA IS RETRIEVED OR ALTERRED BY USER SERIALZE THE DATA IF NECESSARY *(SEE STAR FOR SPECIFICATION ON THIS, WIP), RETURN DATA TO DATABASE MAKING SURE TO OVERWRITE EXISTING ENTRY AND NOT APPENDING (DUE TO THE NATURE OF BRANCHING A VARIABLE ADDRESS POINTER SPACE MUST BE USED WITHIN USER ROWS TO FIND QUIZ ANSWERS PROPERLY)


# * DATA THAT CURRENTLY REQUIRES SERIALIZATION ARE ON TABLE "USER_RESPONSES" AND ARE COLUMNS: "quizzes_to_do", "quizzes_completed", "user_answers" THESE WILL BE EVENTUALLY WRAPPED IN A BEHAVIOR THAT DOES NOT ALLOW THEM TO EXIST IN THE INCORRECT STATE IN THE INCORRECT LOCATION BUT FOR NOW THIS MUST BE DONE MANUALLY. 




"""lookup table is gonna be in csv format for efficiency in python"""
"""ROW: u_id, #completed_quizzes, quizzes_to_do[q_id], quizzes_completed[(q_id, len_quiz)], user_answers[(ques_id, answer)]"""
TEST_STRING = '''  {
 "userID": "TEST_ID",
 "quizID": "5d8256bb-d74c-46a6-9c97-30145f95b580",
 "quizCategories": [
  {
   "id": "3bn9c31",
   "questions": [
    {
     "id": "u0kiecz",
     "UserAnswer": [
      {
       "text": "Yes",
       "id": "zeczju4"
      }
     ]
    },
    {
     "id": "4ooszh1",
     "UserAnswer": [
      {
       "text": "I am ready to jump in with resume prep, finding opportunities, and the like (I am all good with my major).",
       "id": "sscm989"
      }
     ]
    },
    {
     "id": "9koq704",
     "UserAnswer": [
      {
       "text": "Good, and I am contemplating a minor.",
       "id": "6mrbvnt"
      }
     ]
    },
    {
     "id": "yh0p7s3",
     "UserAnswer": [
      {
       "text": "Great! Just needs some polishing.",
       "id": "yez1vla"
      }
     ]
    },
    {
     "id": "bvdy90w",
     "UserAnswer": []
    },
    {
     "id": "5vclacn",
     "UserAnswer": [
      {
       "text": "too bad",
       "id": "es9br45"
      }
     ]
    },
    {
     "id": "upq8ks6",
     "UserAnswer": [
      {
       "text": "Yes (or at least I should be...)",
       "id": "svaf2sp"
      }
     ]
    },
    {
     "id": "t0h46us",
     "UserAnswer": []
    },
    {
     "id": "fegxzsv",
     "UserAnswer": [
      {
       "text": "It sounds familiar. I might have logged in before??",
       "id": "8b6xw8z"
      }
     ]
    },
    {
     "id": "u4vvqgj",
     "UserAnswer": []
    },
    {
     "id": "nnpeobg",
     "UserAnswer": []
    },
    {
     "id": "vj26zkg",
     "UserAnswer": [
      {
       "text": "College of Engineering & Mathematical Sciences (CEMS)",
       "id": "f8gj19u"
      }
     ]
    },
    {
     "id": "5hkon21",
     "UserAnswer": []
    },
    {
     "id": "3aweedc",
     "UserAnswer": []
    },
    {
     "id": "jpn9b9t",
     "UserAnswer": []
    },
    {
     "id": "mzb8f1p",
     "UserAnswer": []
    },
    {
     "id": "8pmjogw",
     "UserAnswer": []
    },
    {
     "id": "dn7cjur",
     "UserAnswer": []
    },
    {
     "id": "ueukpi2",
     "UserAnswer": []
    },
    {
     "id": "8fma18c",
     "UserAnswer": []
    },
    {
     "id": "ktctu5c",
     "UserAnswer": []
    },
    {
     "id": "ala00ck",
     "UserAnswer": [
      {
       "text": "ejorr@uvm.edu"
      }
     ]
    }
   ]
  }
 ]
}       
'''
TEST_STRING_TWO = ''' {
 "userID": "1",
 "quizID": "605ab9c6-4087-496f-b0f9-03e736387715",
 "timeStamp": "Fri, 26 Jun 2026 19:35:33 GMT",
 "quizCategories": [
  {
   "id": "lwao6ai",
   "questions": [
    {
     "id": "clippn2",
     "UserAnswer": [
      {
       "text": "HI",
       "id": "m36a7h0"
      }
     ]
    },
    {
     "id": "zaxz8fd",
     "UserAnswer": [
      {
       "text": "c",
       "id": "qhlk9ks"
      }
     ]
    }
   ]
  }
 ]
}'''

# Exception type for catching database loading and converting on bad types
class IncompatibleType(Exception):
        def __init__(self, message):
            super().__init__(message)


class TypeCheck:
    def __init__(self):
            pass

    def import_data(self, data):
        if type(data) is bytes:
            return pickle.loads(data)
        else:
            raise IncompatibleType(f"Unable to transform data: {type(data)} from bytes to {type(data)}.")
    def export_data(self, data):
        if type (data) in [list, tuple, dict]:
            return pickle.dumps(data)
        else:
            raise IncompatibleType(message=f"Data is of type: {type(data)}, must be of type '<class 'bytes'>'")
        

def connecting_to_sql():
    conn = sqlite3.connect("career_quiz.db")
    cur = conn.cursor()
    return conn, cur
#MUST BE PERFORMED ON ALL LISTS PRIOR TO ADDITION TO DB -- these are now safer
def serialize(data):
    return TypeCheck().export_data(data)
#MUST BE DONE ON ALL SERIALIZATIONS PRIOR TO MODIFICATION
def return_from_serial(data):
    return TypeCheck().import_data(data)
#------------------------- from quiz_preview.js fn -> formatQuizResultsJSON() -> call the below function -- def quiz_complete()
def _json_data_convert(json_string: str):
        quiz_results = json.loads(json_string)
        user_id = quiz_results["userID"]
        quiz_id = quiz_results["quizID"]
        questions = quiz_results["quizCategories"][0]["questions"]
        answers = []
        for answer in questions:
            try:

                if len(answer["UserAnswer"]) > 0:
                    ques_id = answer["id"]    
                    response = answer["UserAnswer"][0]["text"]
                    ans_id = answer["UserAnswer"][0]["id"]
                    answers.append((ques_id, ans_id, response))
                else:
                    answers.append((answer["id"], "NULL_ID", "IDX_ERR"))
            except KeyError:
                answers.append(("NULL_ID", "KEY_ERR", answer["UserAnswer"][0]["text"]))
                continue    
        len_quiz= len(questions)

        return (user_id, quiz_id, len_quiz, answers)





def _increment_quiz_ctr(u_id: str):
    conn, cur = connecting_to_sql()
    query = """UPDATE USER_RESPONSES SET num_completed_quizzes += 1 WHERE u_ID = ?"""
    cur.execute(query, (u_id,))
    conn.commit()
    conn.close()

def _move_quiz_id_todo_cmp(u_id, q_id, len_quiz):
    conn, cur = connecting_to_sql()
    query = """SELECT quizzes_to_do FROM USER_RESPONSES WHERE u_ID = ?"""
    #TODO: more
    cur.execute(query, (u_id,))
    todo = cur.fetchone()
    todo = return_from_serial(todo)
    query = """SELECT completed_quizzes FROM USER_RESPONSE WHERE u_ID = ?"""
    cmp = cur.execute(query, (u_id,))
    cmp = return_from_serial(cmp)
    for i in range(len(todo)):
        if todo[i][0] == q_id:
            _ = todo[i].pop()
            cmp.append((q_id, len_quiz))
    todo = serialize(todo)
    cmp = serialize(cmp)
    cur.execute("UPDATE USER_RESPONSE SET quizzes_to_do = ?, completed_quizzes = ? WHERE u_ID = ?", (todo, cmp, u_id))
    conn.commit()
    conn.close()

def _append_answers(u_id, answer_list):
    conn,cur = connecting_to_sql()
    query = """SELECT user_answers FROM USER_RESPONSE WHERE u_ID = ?"""
    cur.execute(query, (u_id))
    u_ans = cur.fetchone()
    u_ans = return_from_serial(u_ans)
    updated_ans = u_ans.append(answer_list)
    updated_ans = serialize(updated_ans)
    cur.execute("UPDATE USER_RESPONSE SET user_answers = ? WHERE u_ID = ?", (updated_ans, u_id))
    conn.commit()
    conn.close()

def quiz_complete(json_string):
       u_id, q_id, len_quiz, answer_arr = _json_data_convert(json_string)
       _increment_quiz_ctr(u_id)
       _move_quiz_id_todo_cmp(u_id, q_id, len_quiz)
       _append_answers(u_id, answer_arr)


    # -----------------HELPER FUNCTIONS------------------------
def csv_lookup_to_list(topic ,filename="question_keyword_lookup.csv")-> list:
    result = []
    with open(filename, newline = '') as file_:
        filereader = csv.reader(file_)
        for row in filereader:
            if topic == row[0]:
                result.append(row[1:])
            else:
                result.append(f"no results for : {topic}")
    return result
        # admin can lookup keywords and will provide questions that relate to that, then can be queried for. 

def check_user_lookup_status(admin_id, u_id):

        # check to see if all users are accessible to admin, should kill the request to data 
        return True

# -----------------LOOKUP BEHAVIORS------------------------
def findall_users_cmp_quiz(user_id_array: list, quiz_id):
    # query completed_quizzes from user array
    # fetch data -- return from serial
    users_completed = []
    data = "query response"
    for idx, user in enumerate(user_id_array):
        for quiz in data[idx]:
            if quiz[0] == quiz_id:
                if user not in users_completed:
                    users_completed.append(user)

def get_user_response_to_quiz(u_id, q_id):
    conn, cur = connecting_to_sql()
    query = """SELECT num_completed_quizzes, completed_quizzes, user_answers FROM USER_RESPONSE WHERE u_ID = ?"""
    cur.execute(query, (u_id,))
    num_cmp_quiz, completed_quizzes, user_answers = cur.fetchone()
    conn.close()
    completed_quizzes = return_from_serial(completed_quizzes)
    user_answers = return_from_serial(user_answers)
    offset= 0
    end= 0
    for i in range(len(completed_quizzes)):
        if completed_quizzes[i][0] == q_id:
            offset= sum(completed_quizzes[:i-1][1])
            end= offset + completed_quizzes[i][1]
    curr_quiz_answers = user_answers[offset:end]
    return curr_quiz_answers
    
def get_user_responses_of_question_id(ques_id, user_id_array):
    conn, cur = connecting_to_sql()
    responses = []
    query = """SELECT completed_quizzes, user_answers FROM USER_RESPONSE WHERE u_ID IN ?"""
    """this query returns json that looks like [
    {cmp_quizzes}, {user_answers}
    ...]
    for each user in the query"""
    cur.execute(query, (user_id_array,))
    result = cur.fetchall()
    conn.close()
    result = return_from_serial(result)
    for user_index, user in enumerate(result):
        for ques in user[1]:
            if ques[0] == ques_id:
                responses.append((user_id_array[user_index], ques[1]))
                

    return responses
            
def get_users_completed_quiz_quiz_id(user_id_array, q_id):
    result = []
    #TODO: query
    response = ""
    response = return_from_serial(response)
    for idx, user in (user_id_array):
        for quiz in response[idx]:
            if quiz[0]== q_id:
                result.append(user)

        return result
def lookup_kw_arg_on_user_set(keyword:str , user_array: list):
    ques_ids = csv_lookup_to_list(keyword)
    result = []
    for user in user_array:
        # lookup user_responses
        usr_responses = [] # query
        user_responses_in_topic = []
        for ques in usr_responses:
            if ques[0] in ques_ids:
                user_responses_in_topic.append(ques)
        if len(user_responses_in_topic) > 0:
            result.append((user, user_responses_in_topic))

    return result

def lookup_user_todo_completed_quizzes(u_id: str):
    conn, cur = connecting_to_sql()

    query = """SELECT quizzes_assigned, quizzes_completed FROM USER_RESPONSES WHERE U_ID = ?"""
    returned_results = []
    cur.execute(query, (u_id,))
    result = cur.fetchone()
    conn.close()
    if result is not None:
        for item in result:
            returned_results.append(return_from_serial(item))
        if len(result) == 2:
            quiz_ids = [quiz[0] for quiz in result[1]]
            return (result[0], quiz_ids)
    else:
        return (["err"], ["could not fetch data"])

# ------------------------------------------------TEST-CODE------------------------------------------------#
# ------------------------------------------------TEST-CODE------------------------------------------------#
# ------------------------------------------------TEST-CODE------------------------------------------------#

def quiz_id_to_quiz_title_translator(quiz_id, quiz_folder_MASTER):
    '''
    Translation function to get quiz title from inputting the quiz ID

    :param quiz_folder_MASTER: The name of the folder that holds the JSON files for the quizzes

    :returns: quiz title in text form
    '''

    # Finds matching JSON file in the master folder
    quiz_file_name = f'{quiz_id}.json'
    file_path = os.path.join(quiz_folder_MASTER, quiz_file_name)

    if os.path.exists(file_path):
        #print(f"Opening and parsing: {file_path}") TEST CODE

        # opens quiz json file
        with open(file_path, "r", encoding="utf-8") as file:
            quiz_data = json.load(file)
            return quiz_data['title']
    else:
        print(f" Error: The file {file_path} could not be found.")
        
def question_id_to_text_translator(quiz_id, answers_id_list, quiz_folder_MASTER):
    '''
    Translation function to get question text from question IDs

    :param answer_id_list: List of tuples in format [(question_id, answer_id, answer_text), ...]
    :param quiz_folder_MASTER: The name of the folder that holds the JSON files for the quizzes

    :returns: A list of all the questions from the quiz in text form
    '''

    # Finds matching JSON file in the master folder
    quiz_file_name = f'{quiz_id}.json'
    file_path = os.path.join(quiz_folder_MASTER, quiz_file_name)
    
    # parse answer_id_list to get question ids
    QUESTION_ID_INDEX = 0
    question_ids = []
    for answer in answers_id_list:
        question_ids.append(answer[QUESTION_ID_INDEX])

    # where the text for the questions will be stored
    question_text = []
    if os.path.exists(file_path):
        #print(f"Opening and parsing: {file_path}") TEST CODE

        # opens quiz json file
        with open(file_path, "r", encoding="utf-8") as file:
            quiz_data = json.load(file)
        
        # matches question id's and pulls text
        for category in quiz_data["categories"]:
            for item in category["items"]:
                counter = 0
                while item['id'] != question_ids[counter]:
                    counter += 1
                
                # Failsafe against infinite loops
                if counter == len(question_ids):
                    question_text.append('NO MATCH SOMETHING IS BROKEN')
                    break
                question_text.append(item['text'])
        return question_text  
    else:
        print(f" Error: The file {file_path} could not be found.")
# ------------------------------------------------TEST-CODE------------------------------------------------#
# ------------------------------------------------TEST-CODE------------------------------------------------#
# ------------------------------------------------TEST-CODE------------------------------------------------#


if __name__ == "__main__":
    #gerald = _json_data_convert(TEST_STRING_TWO)
    #print(gerald)

    # (question_id, answer_id, answer_text)
    TEST_QUIZ_ANSWERS = [('wu2k8f4', 't2u0y1r', 'HELLO'), ('umdk5o3', '43zaysu', 'Dragon Fruit'), ('5u83jdb', 'umo3d5g', 'VT')]

    TEST_QUIZ_ID = 'pjo4roy'

    print('-'*15 + 'QUIZ TITLE' + '-'*15)
    print(quiz_id_to_quiz_title_translator(TEST_QUIZ_ID, 'testing_quiz'))
    print('-'*43)
    print('-'*15 + 'QUESTION TEXT' + '-'*15)
    print(question_id_to_text_translator(TEST_QUIZ_ID, TEST_QUIZ_ANSWERS, 'testing_quiz'))
    print('-'*43)