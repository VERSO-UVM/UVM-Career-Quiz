"""
Create the database. WARNING : CALLING ANY FUNCTION HERE WILL ESENTIALLY WIPE ALL DATA.
To be used by an admin to wipe all data
"""

import sqlite3



def user_creation(cur):
    cur.execute('''DROP TABLE IF EXISTS USER''')
    cur.execute('''CREATE TABLE USER(u_ID TEXT NOT NULL UNIQUE, Username TEXT NOT NULL UNIQUE , Password TEXT NOT NULL,PRIMARY KEY("u_ID"))''')

def quiz_creation(cur):
    cur.execute('''DROP TABLE IF EXISTS QUIZ''')
    cur.execute('''CREATE TABLE QUIZ(q_ID TEXT NOT NULL UNIQUE, name TEXT NOT NULL UNIQUE,PRIMARY KEY("q_ID"))''')

def acess_creation(cur):
    cur.execute('''DROP TABLE IF EXISTS ACESS''')
    cur.execute('''CREATE TABLE ACESS(u_ID TEXT NOT NULL UNIQUE, q_id TEXT NOT NULL UNIQUE )''')

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