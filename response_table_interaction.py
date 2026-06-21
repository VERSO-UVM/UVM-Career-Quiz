import json
import sqlite3
import csv
import pickle
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
        len_quiz= len(questions)

        return (user_id, quiz_id, len_quiz, answers)





def _incriment_quiz_ctr(u_id: str):
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
       _incriment_quiz_ctr(u_id)
       _move_quiz_id_todo_cmp(u_id, q_id, len_quiz)
       _append_answers(u_id, answer_arr)


    # -----------------HELPER FUNCTIONS------------------------
def csv_lookup_to_dict():
        # admin can lookup keywords and will provide questions that relate to that, then can be queried for. 
        pass
def check_user_lookup_status(admin_id, u_id):
        # check to see if all users are accessible to admin, should kill the request to data 
        pass
def data_type_correction_wrapper():
    #this will eventually be a class for data but not yet just a placeholder see * above for more information
    pass
    # -----------------LOOKUP BEHAVIORS------------------------
def findall_users_cmp_quiz():
        pass
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
    
def get_response_breakdown_on_users(ques_id, user_id_array, q_id):
    conn, cur = connecting_to_sql()
    responses = []

    query = """SELECT completed_quizzes, user_answers FROM USER_RESPONSE WHERE u_ID IN ?"""
    cur.execute(query, (user_id_array,))
    user_comp_quizzes, user_answers = cur.fetchall()
    conn.close()
    user_comp_quizzes = return_from_serial(user_comp_quizzes)
    user_answers = return_from_serial(user_answers)
    for user in user_comp_quizzes:
        for quiz in user:
            if quiz[0] == q_id:
                pass


            
        # loop through user checking
        #1. is q_id in user completed quizzes
        #2. if so, fetch the user responses to the quizzes (get_user_response_to_quiz)
        #3. check to see if question id in list of responses, this can sometimes not happen because of branching
        # append user_id, question_response to responses where u_id 
def fetch_results_of_question_id_on_user_set():
        pass
def lookup_kw_arg_on_user_set():
        pass

    

if __name__ == "__main__":
    gerald = _json_data_convert(TEST_STRING)
    print((gerald))

