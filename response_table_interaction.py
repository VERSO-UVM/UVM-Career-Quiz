import json
import sqlite3
import csv
import pickle
from typing import Any
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
        if isinstance(data ,bytes):
            return pickle.loads(data)
        else:
            raise IncompatibleType(f"Unable to transform data: {type(data)} from bytes to {type(data)}.")
    def export_data(self, data):
        if isinstance(data, (list, tuple, dict)):
            return pickle.dumps(data)
        else:
            # maybe we don't need this, looking to see if data can just be grabbed off a catch when no serialization is needed
            return data
"""
            raise IncompatibleType(message=f"Data is of type: {type(data)}, must be of type '<class 'bytes'>'")
"""
# --------------------------------------- GENERIC QUERY TEST -----------------------------------------------------------------------
def __generic_query_response(ptr_t_cursor, query, func,  write_query, read_args, write_args=None, write=False, fn_val=None):
    conn, cur = ptr_t_cursor()
    try:
        if len(read_args) == 1:
            cur.execute(query, (read_args[0],))
            dat = cur.fetchone()
        else:
            cur.execute(query, tuple(read_args))
            dat = cur.fetchall()

        dat = _deserialize_db_row(dat)
        _dat = dat
        if isinstance(dat, tuple) and len(dat) == 1:
            dat = dat[0]
        elif isinstance(dat, list):
            dat = [
                item[0] if isinstance(item, tuple) and len(item) == 1 else item
                for item in dat
            ]
        if callable(func):
            if fn_val is None:
                dat = func(dat)
            else:
                if write_args is None:
                    dat = func(fn_val, dat)
                else:
                    write_args[0] = func(write_args[0], dat)

        if write and write_args:
            write_args = (serialize(write_args[0]), write_args[1])
            cur.execute(write_query, write_args)
            conn.commit()
            

        return _dat
    finally:
        conn.close()




# not sure if this will work but we'll see 
# ------------------------------------------------------------------------------------------------------------------------------------
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



def _deserialize_db_value(value):
    if isinstance(value, (bytes, bytearray)):
        return return_from_serial(value)
    return value

def _deserialize_db_row(row):
    if isinstance(row, tuple):
        return tuple(_deserialize_db_value(item) for item in row)
    if isinstance(row, list):
        return [_deserialize_db_value(item) for item in row]
    return _deserialize_db_value(row)


def _fetch_ordered_user_rows(user_id_array: list, columns: str):
    if not user_id_array:
        return []

    conn, cur = connecting_to_sql()
    try:
        placeholders = ", ".join("?" for _ in user_id_array)
        query = f"SELECT u_ID, {columns} FROM USER_RESPONSES WHERE u_ID IN ({placeholders})"
        cur.execute(query, tuple(user_id_array))
        fetched_rows = cur.fetchall()
    finally:
        conn.close()

    row_map = {row[0]: _deserialize_db_row(row[1:]) for row in fetched_rows}
    ordered_rows = []
    for u_id in user_id_array:
        if u_id in row_map:
            ordered_rows.append((u_id, *row_map[u_id]))
    return ordered_rows


def _fetch_user_response_record(u_id: str):
    conn, cur = connecting_to_sql()
    try:
        cur.execute(
            """
            SELECT num_completed_quizzes, quizzes_assigned, quizzes_completed, quiz_response_answers
            FROM USER_RESPONSES
            WHERE u_ID = ?
            """,
            (u_id,),
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    num_completed_quizzes, quizzes_assigned, quizzes_completed, quiz_response_answers = _deserialize_db_row(row)
    return {
        "num_completed_quizzes": num_completed_quizzes or 0,
        "quizzes_assigned": quizzes_assigned or [],
        "quizzes_completed": quizzes_completed or [],
        "quiz_response_answers": quiz_response_answers or [],
    }


def _sync_legacy_user_response_table(
    u_id: str,
    num_completed_quizzes,
    quizzes_to_do,
    completed_quizzes,
    user_answers,
):
    conn, cur = connecting_to_sql()
    try:
        cur.execute(
            """
            UPDATE USER_RESPONSE
            SET num_completed_quizzes = ?,
                quizzes_to_do = ?,
                completed_quizzes = ?,
                user_answers = ?
            WHERE u_ID = ?
            """,
            (
                num_completed_quizzes,
                serialize(quizzes_to_do),
                serialize(completed_quizzes),
                serialize(user_answers),
                u_id,
            ),
        )
        conn.commit()
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()


def _sync_user_response_state(
    u_id: str,
    num_completed_quizzes,
    quizzes_assigned,
    quizzes_completed,
    quiz_response_answers,
):
    conn, cur = connecting_to_sql()
    try:
        cur.execute(
            """
            UPDATE USER_RESPONSES
            SET num_completed_quizzes = ?,
                quizzes_assigned = ?,
                quizzes_completed = ?,
                quiz_response_answers = ?
            WHERE u_ID = ?
            """,
            (
                num_completed_quizzes,
                serialize(quizzes_assigned),
                serialize(quizzes_completed),
                serialize(quiz_response_answers),
                u_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    _sync_legacy_user_response_table(
        u_id,
        num_completed_quizzes,
        quizzes_assigned,
        quizzes_completed,
        quiz_response_answers,
    )

#------------------------- from quiz_preview.js fn -> formatQuizResultsJSON() -> call the below function -- def quiz_complete()

def user_assigned_new_quiz(u_id: str, q_id: str):
    def append_on(tail, data):
        return data.append(tail)
    #testing generic query here
    data = __generic_query_response(connecting_to_sql, 
                             "SELECT quizzes_assigned FROM USER_RESPONSES WHERE u_ID = ?",
                             append_on,
                             "UPDATE USE_RESPONSES SET quizzes_assigned = ? WHERE u_ID = ?",
                             u_id,
                             write_args= (q_id ,u_id),
                             write=True)




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
    try:
        cur.execute(
            """
            UPDATE USER_RESPONSES
            SET num_completed_quizzes = COALESCE(num_completed_quizzes, 0) + 1
            WHERE u_ID = ?
            """,
            (u_id,),
        )
        conn.commit()
    finally:
        conn.close()

def _move_quiz_id_todo_cmp(u_id, q_id, len_quiz):
    record = _fetch_user_response_record(u_id)
    if record is None:
        return

    quizzes_assigned = list(record["quizzes_assigned"])
    quizzes_completed = list(record["quizzes_completed"])
    quiz_response_answers = list(record["quiz_response_answers"])

    quizzes_assigned = [quiz for quiz in quizzes_assigned if quiz != q_id]
    if not any(quiz[0] == q_id for quiz in quizzes_completed):
        quizzes_completed.append((q_id, len_quiz))

    _sync_user_response_state(
        u_id,
        record["num_completed_quizzes"],
        quizzes_assigned,
        quizzes_completed,
        quiz_response_answers,
    )

def _append_answers(u_id, answer_list):
    record = _fetch_user_response_record(u_id)
    if record is None:
        return

    quiz_response_answers = list(record["quiz_response_answers"])
    quiz_response_answers.extend(answer_list)

    _sync_user_response_state(
        u_id,
        record["num_completed_quizzes"],
        record["quizzes_assigned"],
        record["quizzes_completed"],
        quiz_response_answers,
    )

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
            if not row:
                continue
            if topic == row[0]:
                result.extend(row[1:])
    return result
        # admin can lookup keywords and will provide questions that relate to that, then can be queried for. 

def check_user_lookup_status(admin_id, u_id):
    #TODO asap probably 

        # check to see if all users are accessible to admin, should kill the request to data 
        return True

# -----------------LOOKUP BEHAVIORS------------------------
#TODO: WARNING NOT DONE
def findall_users_cmp_quiz(user_id_array: list, quiz_id):
    users_completed = []
    ordered_rows = _fetch_ordered_user_rows(user_id_array, "quizzes_completed")
    for u_id, quizzes_completed in ordered_rows:
        if any(quiz[0] == quiz_id for quiz in quizzes_completed):
            users_completed.append(u_id)
    return users_completed

def get_user_response_to_quiz(u_id, q_id):
    conn, cur = connecting_to_sql()
    try:
        query = """SELECT quizzes_completed, quiz_response_answers FROM USER_RESPONSES WHERE u_ID = ?"""
        cur.execute(query, (u_id,))
        row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return []

    completed_quizzes, user_answers = _deserialize_db_row(row)
    offset = 0
    for quiz_id, quiz_len in completed_quizzes:
        if quiz_id == q_id:
            return user_answers[offset:offset + quiz_len]
        offset += quiz_len
    return []
    
def get_user_responses_of_question_id(ques_id, user_id_array):
    responses = []
    ordered_rows = _fetch_ordered_user_rows(user_id_array, "quiz_response_answers")
    for u_id, user_answers in ordered_rows:
        matching = [answer for answer in user_answers if answer[0] == ques_id]
        if matching:
            responses.append((u_id, matching))
    return responses
            
def get_users_completed_quiz_quiz_id(user_id_array, q_id):
    result = []
    ordered_rows = _fetch_ordered_user_rows(user_id_array, "quizzes_completed")
    for u_id, quizzes_completed in ordered_rows:
        if any(quiz[0] == q_id for quiz in quizzes_completed):
            result.append(u_id)
    return result
def lookup_kw_arg_on_user_set(keyword:str , user_array: list):
    ques_ids = set(csv_lookup_to_list(keyword))
    result = []
    ordered_rows = _fetch_ordered_user_rows(user_array, "quiz_response_answers")
    for user, usr_responses in ordered_rows:
        user_responses_in_topic = [
            ques for ques in usr_responses
            if ques[0] in ques_ids
        ]
        if len(user_responses_in_topic) > 0:
            result.append((user, user_responses_in_topic))

    return result

def lookup_user_todo_completed_quizzes(u_id: str):
    record = _fetch_user_response_record(u_id)
    if record is None:
        return ([], [])

    completed_ids = [quiz[0] for quiz in record["quizzes_completed"]]
    assigned = [
        quiz_id for quiz_id in record["quizzes_assigned"]
        if quiz_id not in completed_ids
    ]
    return (assigned, completed_ids)

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
 


def _api_normalize_value(value: Any):
    if isinstance(value, dict):
        return {str(key): _api_normalize_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_api_normalize_value(item) for item in value]
    if isinstance(value, list):
        return [_api_normalize_value(item) for item in value]
    return value


def _api_response(action: str, data=None, **meta):
    payload = {
        "ok": True,
        "action": action,
        "data": _api_normalize_value(data),
    }
    for key, value in meta.items():
        if value is not None:
            payload[key] = _api_normalize_value(value)
    return payload


def _api_error(action: str, message: str, **meta):
    payload = {
        "ok": False,
        "action": action,
        "error": message,
    }
    for key, value in meta.items():
        if value is not None:
            payload[key] = _api_normalize_value(value)
    return payload


# this is the head pointer to this file, all dashboard functions should be able to be called from here
def api_header(action: str = None, **kwargs):
    """
    Unified entry point for database/report lookups.

    The header returns dictionaries for every supported query so callers do
    not need to sequence lower-level helpers manually. Known calls preserve the
    shape of the underlying helper data, but the outer result is always a dict.
    """
    if action is None:
        action = kwargs.pop("query", None) or kwargs.pop("request", None) or kwargs.pop("report", None)

    if not action:
        return _api_error("unknown", "Missing action/query name.")

    action = str(action)

    try:
        if action in {"lookup_user_todo_completed_quizzes", "user_quiz_status"}:
            u_id = kwargs["u_id"]
            assigned, completed = lookup_user_todo_completed_quizzes(u_id)
            response = {
                "user_id": u_id,
                "assigned": assigned,
                "completed": completed,
            }
            quiz_folder = kwargs.get("quiz_folder_MASTER")
            if quiz_folder:
                response["assigned_titles"] = [
                    {
                        "quiz_id": quiz_id,
                        "title": quiz_id_to_quiz_title_translator(quiz_id, quiz_folder),
                    }
                    for quiz_id in assigned
                ]
                response["completed_titles"] = [
                    {
                        "quiz_id": quiz_id,
                        "title": quiz_id_to_quiz_title_translator(quiz_id, quiz_folder),
                    }
                    for quiz_id in completed
                ]
            return _api_response(action, response)

        if action in {"get_user_response_to_quiz", "user_quiz_responses"}:
            u_id = kwargs["u_id"]
            q_id = kwargs["q_id"]
            answers = get_user_response_to_quiz(u_id, q_id)
            response = {
                "user_id": u_id,
                "quiz_id": q_id,
                "answers": answers,
            }
            quiz_folder = kwargs.get("quiz_folder_MASTER")
            if quiz_folder:
                response["quiz_title"] = quiz_id_to_quiz_title_translator(q_id, quiz_folder)
                response["question_text"] = question_id_to_text_translator(q_id, answers, quiz_folder)
            return _api_response(action, response)

        if action in {"findall_users_cmp_quiz", "get_users_completed_quiz_quiz_id"}:
            user_id_array = kwargs["user_id_array"]
            q_id = kwargs["q_id"]
            users = get_users_completed_quiz_quiz_id(user_id_array, q_id)
            return _api_response(action, {
                "quiz_id": q_id,
                "user_ids": users,
            })

        if action == "get_user_responses_of_question_id":
            ques_id = kwargs["ques_id"]
            user_id_array = kwargs["user_id_array"]
            responses = get_user_responses_of_question_id(ques_id, user_id_array)
            return _api_response(action, {
                "question_id": ques_id,
                "responses": responses,
            })

        if action == "lookup_kw_arg_on_user_set":
            keyword = kwargs["keyword"]
            user_array = kwargs["user_array"]
            responses = lookup_kw_arg_on_user_set(keyword, user_array)
            return _api_response(action, {
                "keyword": keyword,
                "responses": responses,
            })

        if action == "quiz_id_to_quiz_title_translator":
            quiz_id = kwargs["quiz_id"]
            quiz_folder_MASTER = kwargs["quiz_folder_MASTER"]
            title = quiz_id_to_quiz_title_translator(quiz_id, quiz_folder_MASTER)
            return _api_response(action, {
                "quiz_id": quiz_id,
                "title": title,
            })

        if action == "question_id_to_text_translator":
            quiz_id = kwargs["quiz_id"]
            answers_id_list = kwargs["answers_id_list"]
            quiz_folder_MASTER = kwargs["quiz_folder_MASTER"]
            question_text = question_id_to_text_translator(quiz_id, answers_id_list, quiz_folder_MASTER)
            return _api_response(action, {
                "quiz_id": quiz_id,
                "questions": question_text,
            })

        if action == "quiz_report":
            u_id = kwargs["u_id"]
            q_id = kwargs["q_id"]
            quiz_folder = kwargs.get("quiz_folder_MASTER")
            answers = get_user_response_to_quiz(u_id, q_id)
            assigned, completed = lookup_user_todo_completed_quizzes(u_id)
            response = {
                "user_id": u_id,
                "quiz_id": q_id,
                "assigned": assigned,
                "completed": completed,
                "answers": answers,
            }
            if quiz_folder:
                response["quiz_title"] = quiz_id_to_quiz_title_translator(q_id, quiz_folder)
                response["question_text"] = question_id_to_text_translator(q_id, answers, quiz_folder)
            return _api_response(action, response)

        if action == "question_report":
            ques_id = kwargs["ques_id"]
            user_id_array = kwargs["user_id_array"]
            responses = get_user_responses_of_question_id(ques_id, user_id_array)
            return _api_response(action, {
                "question_id": ques_id,
                "responses": responses,
            })

        if action == "keyword_report":
            keyword = kwargs["keyword"]
            user_array = kwargs["user_array"]
            responses = lookup_kw_arg_on_user_set(keyword, user_array)
            return _api_response(action, {
                "keyword": keyword,
                "responses": responses,
            })

        return _api_error(action, f"Unsupported action: {action}")
    except KeyError as exc:
        return _api_error(action, f"Missing required parameter: {exc.args[0]}")
    except Exception as exc:
        return _api_error(action, f"{type(exc).__name__}: {exc}")
if __name__ == "__main__":
    #gerald = _json_data_convert(TEST_STRING_TWO)
    #print(gerald)

    # (question_id, answer_id, answer_text)
    TEST_QUIZ_ANSWERS = [('wu2k8f4', 't2u0y1r', 'HELLO'), ('umdk5o3', '43zaysu', 'Dragon Fruit'), ('5u83jdb', 'umo3d5g', 'VT')]

    TEST_QUIZ_ID = 'pjo4roy'

    MASTER_FILE_NAME = 'testing_quiz'

    print('-'*15 + 'QUIZ TITLE' + '-'*15)
    print(quiz_id_to_quiz_title_translator(TEST_QUIZ_ID, MASTER_FILE_NAME))
    print('-'*43)
    print('-'*15 + 'QUESTION TEXT' + '-'*15)
    print(question_id_to_text_translator(TEST_QUIZ_ID, TEST_QUIZ_ANSWERS, MASTER_FILE_NAME))
    print('-'*43)
