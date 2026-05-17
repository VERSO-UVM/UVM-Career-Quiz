"""
Create the database. WARNING : CALLING ANY FUNCTION HERE WILL ESENTIALLY WIPE ALL DATA.
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
    cur.execute('''CREATE TABLE QUIZ(q_ID TEXT NOT NULL UNIQUE, name TEXT NOT NULL UNIQUE,PRIMARY KEY("q_ID"))''')

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

if __name__ == "__main__":
    conn = sqlite3.connect("carrer_quiz.db")
    cur = conn.cursor()
    user_creation(cur)
    conn.commit()
    quiz_creation(cur)
    conn.commit()
    acess_creation(cur)
    conn.commit()
    conn.close()