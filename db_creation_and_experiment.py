"""
Create the database. WARNING : CALLING CREATE_DB() WILL ESENTIALLY WIPE ALL DATA.
To be used by an admin to wipe all data
"""

import sqlite3

def connecting_to_sql():
    conn = sqlite3.connect("carrer_quiz.db")
    cur = conn.cursor()
    return conn,cur

    

def user_creation(cur):
    cur.execute('''DROP TABLE IF EXISTS USER''')
    cur.execute('''CREATE TABLE USER(u_ID TEXT NOT NULL UNIQUE, Username TEXT NOT NULL UNIQUE , Password TEXT NOT NULL,PRIMARY KEY("u_ID"))''')

def quiz_creation(cur):
    cur.execute('''DROP TABLE IF EXISTS QUIZ''')
    cur.execute('''CREATE TABLE QUIZ(q_ID TEXT NOT NULL UNIQUE, name TEXT NOT NULL,PRIMARY KEY("q_ID"))''')

def acess_creation(cur):
    cur.execute('''DROP TABLE IF EXISTS ACESS''')
    cur.execute('''CREATE TABLE ACESS(u_ID TEXT NOT NULL, q_id TEXT NOT NULL )''')

def find_name_with_id(q_id):
    conn, cur = connecting_to_sql()
    query = "SELECT name FROM QUIZ WHERE q_ID = ?"
    cur.execute(query,(q_id,))
    row = cur.fetchall()

    conn.close()
    if row : 
        return row[0][0]
    else :
        return ""  

#TODO both this and the find_name_with_id function need to be worked on so that user acces is taken into account.For now it's a free for all though
def save_quiz_in_the_db(q_id, q_title):
    conn, cur = connecting_to_sql()
    query = "SELECT name FROM QUIZ WHERE q_ID = ?"
    cur.execute(query,(q_id,))
    row = cur.fetchall()

    if row :
        cur.execute("UPDATE QUIZ SET name = ? WHERE q_id = ?", (q_title, q_id))
    else: 
        cur.execute("INSERT INTO QUIZ (q_ID, name) VALUES (?,?)", (q_id, q_title))
    conn.commit()
    conn.close()

def create_db():
    id_1 = "1"
    u_name_1 = "1"
    u_pass_1 = "1"
    id_2 = "2"
    u_name_2 = "2"
    u_pass_2 = "2"
    q_id_1 = "pjo4roy"
    name_1 = "testing quiz"
    q_id_2 = "so7kpib"
    name_2 = "abc"
    conn = sqlite3.connect("carrer_quiz.db")
    cur = conn.cursor()
    user_creation(cur)
    cur.execute("INSERT INTO USER (u_ID, Username, Password) VALUES (?,?,?)", (id_1, u_name_1, u_pass_1))
    cur.execute("INSERT INTO USER (u_ID, Username, Password) VALUES (?,?,?)", (id_2, u_name_2, u_pass_2))
    conn.commit()
    quiz_creation(cur)
    cur.execute("INSERT INTO QUIZ (q_ID, name) VALUES (?,?)", (q_id_1, name_1))
    cur.execute("INSERT INTO QUIZ (q_ID, name) VALUES (?,?)", (q_id_2, name_2))
    conn.commit()
    acess_creation(cur)
    cur.execute("INSERT INTO ACESS (u_ID, q_ID) VALUES (?,?)", (id_1, q_id_1))
    cur.execute("INSERT INTO ACESS (u_ID, q_ID) VALUES (?,?)", (id_2, q_id_1))
    cur.execute("INSERT INTO ACESS (u_ID, q_ID) VALUES (?,?)", (id_2, q_id_2))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()