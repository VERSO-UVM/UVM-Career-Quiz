"""
Create the database. Allow manipulation to the DB too.  
WARNING : CALLING CREATE_DB() WILL ESENTIALLY WIPE ALL DATA.
To be used by an admin to wipe all data
"""

import sqlite3


#As it stand you cannot carry sql statement between python file, therefore it will allow us to connect to the DB
def connecting_to_sql():
    conn = sqlite3.connect("carrer_quiz.db")
    cur = conn.cursor()
    return conn,cur

    
# Create the user table
def user_creation(cur):
    cur.execute('''DROP TABLE IF EXISTS USER''')
    cur.execute('''CREATE TABLE USER(u_ID TEXT NOT NULL UNIQUE, Username TEXT NOT NULL UNIQUE , Password TEXT NOT NULL, Email TEXT NOT NULL UNIQUE, PRIMARY KEY("u_ID"))''')

#Create the quiz table
def quiz_creation(cur):
    cur.execute('''DROP TABLE IF EXISTS QUIZ''')
    cur.execute('''CREATE TABLE QUIZ(q_ID TEXT NOT NULL UNIQUE, name TEXT NOT NULL,owner_id TEXT NOT NULL, PRIMARY KEY("q_ID"))''')

#Create the acess table
def acess_creation(cur):
    cur.execute('''DROP TABLE IF EXISTS ACESS''')
    cur.execute('''CREATE TABLE ACESS(u_ID TEXT NOT NULL, q_id TEXT NOT NULL )''')


#Find the name of a quiz with it's ID
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

#Find the user id of a user providing it's username. 
def find_id_with_uname(username):
    conn, cur = connecting_to_sql()
    query = "SELECT u_id FROM USER WHERE Username = ?"

    cur.execute(query,(username,))

    row = cur.fetchone()

    conn.close()

    if row :
        return row[0]
    else :
        return ""

#reverse of the above function
def find_uname_with_id(u_id):
    conn, cur = connecting_to_sql()
    cur.execute("SELECT Username FROM USER WHERE u_ID = ?", (u_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return ""

#Share a quiz with another user
def share_quiz(u_id, q_id):
    conn, cur = connecting_to_sql()
    cur.execute("INSERT INTO ACESS (q_id, u_id) VALUES(?,?) ", (q_id, u_id))
    conn.commit()
    conn.close()

#Save a quiz in the DB
def save_quiz_in_the_db(q_id, q_title, u_ID):
    conn, cur = connecting_to_sql()
    query = "SELECT name FROM QUIZ WHERE q_ID = ?"
    cur.execute(query,(q_id,))
    row = cur.fetchall()

    if row :
        cur.execute("UPDATE QUIZ SET name = ? WHERE q_id = ?", (q_title, q_id))
    else: 
        cur.execute("INSERT INTO QUIZ (q_ID, name, owner_id) VALUES (?,?,?)", (q_id, q_title, u_ID))
        cur.execute("INSERT INTO ACESS (q_id, u_id) VALUES(?,?) ", (q_id, u_ID))
    conn.commit()
    conn.close()


#Return whether or not a User has acess to a quiz or not
def has_acess(u_ID, q_ID):
    conn, cur = connecting_to_sql()
    query = "SELECT * FROM ACESS WHERE q_ID = ? AND u_ID = ?"
    cur.execute(query,(q_ID, u_ID))
    row = cur.fetchone()
    conn.close()
    return row

def user_with_acess(q_id):
    conn, cur = connecting_to_sql()
    query = "SELECT * FROM ACESS WHERE q_ID = ?"
    cur.execute(query,(q_id,))
    row = cur.fetchall()
    conn.close()
    if row:   
        return row
    else: 
        return ""


# Return the username of the quiz creator
def find_creator(q_id):
    conn, cur = connecting_to_sql()
    cur.execute("SELECT Username FROM USER JOIN QUIZ ON USER.u_ID = QUIZ.owner_id WHERE QUIZ.q_ID = ?", (q_id,))
    row = cur.fetchone()
    conn.close()
    if row :
        return row[0]
    else :
        return ""

# Remove a user's access to a quiz
def remove_access(u_id, q_id):
    conn, cur = connecting_to_sql()
    cur.execute("DELETE FROM ACESS WHERE u_ID = ? AND q_ID = ?", (u_id, q_id))
    conn.commit()
    conn.close()

#Call the first 4 function in this file to create the Database. Careful as stated above it wipe all and every data in the DB except for training one
def create_db():
    id_1 = "1"
    u_name_1 = "1"
    u_pass_1 = "1"
    u_mail_1 = "1@1"
    id_2 = "2"
    u_name_2 = "2"
    u_pass_2 = "2"
    u_mail_2 = "2@2"
    q_id_1 = "pjo4roy"
    name_1 = "testing quiz"
    q_id_2 = "so7kpib"
    name_2 = "abc"
    conn, cur = connecting_to_sql()
    user_creation(cur)
    cur.execute("INSERT INTO USER (u_ID, Username, Password,Email) VALUES (?,?,?,?)", (id_1, u_name_1, u_pass_1, u_mail_1))
    cur.execute("INSERT INTO USER (u_ID, Username, Password, Email) VALUES (?,?,?,?)", (id_2, u_name_2, u_pass_2,u_mail_2))
    conn.commit()
    quiz_creation(cur)
    cur.execute("INSERT INTO QUIZ (q_ID, name, owner_id) VALUES (?,?,?)", (q_id_1, name_1, id_1))
    cur.execute("INSERT INTO QUIZ (q_ID, name, owner_id) VALUES (?,?,?)", (q_id_2, name_2, id_2))
    conn.commit()
    acess_creation(cur)
    cur.execute("INSERT INTO ACESS (u_ID, q_ID) VALUES (?,?)", (id_1, q_id_1))
    cur.execute("INSERT INTO ACESS (u_ID, q_ID) VALUES (?,?)", (id_2, q_id_1))
    cur.execute("INSERT INTO ACESS (u_ID, q_ID) VALUES (?,?)", (id_2, q_id_2))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()