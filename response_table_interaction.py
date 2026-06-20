import json
import sqlite3
import csv
import pickle
"""lookup table is gonna be in csv format for efficiency in python"""
"""ROW: u_id, #completed_quizzes, quizzes_to_do[q_id], quizzes_completed[(q_id, len_quiz)], quiz_response_answers[(ques_id, answer)]"""
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
def connecting_to_sql():
    conn = sqlite3.connect("career_quiz.db")
    cur = conn.cursor()
    return conn, cur
#MUST BE PERFORMED ON ALL LISTS PRIOR TO ADDITION TO DB
def serialize(data):
    return pickle.dumps(data)
#MUST BE DONE ON ALL SERIALIZATIONS PRIOR TO MODIFICATION
def return_from_serial(data):
    return pickle.loads(data)

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
                    answers.append((ques_id,"Answer Details: " ,ans_id, response))
                else:
                    answers.append((answer["id"], "NULL_ID", "IDX_ERR"))
            except KeyError:
                answers.append(("NULL_ID", "KEY_ERR", answer["UserAnswer"][0]["text"]))
                continue
    
        len_categories = len(questions)
        
        quiz_categories= [3]
        mcq= []
        slider= []
        text_answer= []
        answer_list= questions
        len_quiz= len(answer_list)

        for answer in answers:
            print(answer)
        print(len(answers))
        return (len_categories, answers)





def _incriment_quiz_ctr(self):
    pass
def _move_quiz_id_todo_cmp(self):
    pass
def _append_ansrewers(self):
    pass

def quiz_complete():
        pass

    # -----------------HELPER FUNCTIONS------------------------
def csv_lookup_to_dict():
        pass
def check_user_lookup_status():
        pass
    # -----------------LOOKUP BEHAVIORS------------------------
def findall_users_cmp_quiz():
        pass
def get_user_response_to_quiz():
        pass
def get_response_breakdown_on_users():
        pass
def fetch_results_of_question_id_on_user_set():
        pass
def lookup_kw_arg_on_user_set():
        pass

    

if __name__ == "__main__":
    #print(_json_data_convert(TEST_STRING))
    serial_data = serialize(_json_data_convert(TEST_STRING)[1])
    std_data = return_from_serial(serial_data)
    print(serial_data)
    print(std_data)
    


        

    
