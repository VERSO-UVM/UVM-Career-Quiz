"""
Create the database. Allow manipulation to the DB too.  
WARNING : CALLING CREATE_DB() WILL ESENTIALLY WIPE ALL DATA.
To be used by an admin to wipe all data
"""

import sqlite3

ROLE_CREATOR = "creator"
ROLE_ADMIN   = "admin"
ROLE_EDITOR  = "editor"
ROLE_READER  = "reader"
ROLE_RANK = { ROLE_CREATOR:4, 
              ROLE_ADMIN:3, 
              ROLE_EDITOR:2, 
              ROLE_READER:1 }

#As it stand you cannot carry sql statement between python file, therefore it will allow us to connect to the DB
def connecting_to_sql():
    conn = sqlite3.connect("carrer_quiz.db")
    cur = conn.cursor()
    return conn,cur
def can_edit(role):   
    return role in (ROLE_CREATOR, ROLE_ADMIN, ROLE_EDITOR)
def can_share(role): 
    return role in (ROLE_CREATOR, ROLE_ADMIN)
def can_delete(role): 
    return role == ROLE_CREATOR
def can_revoke(role): 
    return role in (ROLE_CREATOR, ROLE_ADMIN)
def can_promote(actor_role, target_role):
    if target_role == ROLE_CREATOR: 
        return False
    return ROLE_RANK.get(actor_role,0) > ROLE_RANK.get(target_role,0)
    
# Create the user table
def user_creation(cur):
    cur.execute('''DROP TABLE IF EXISTS USER''')
    cur.execute('''CREATE TABLE USER(u_ID TEXT NOT NULL UNIQUE, Username TEXT NOT NULL UNIQUE , Password TEXT NOT NULL, Email TEXT NOT NULL UNIQUE, PRIMARY KEY("u_ID"))''')

#Create the quiz table
def quiz_creation(cur):
    cur.execute('''DROP TABLE IF EXISTS QUIZ''')
    cur.execute('''CREATE TABLE QUIZ(q_ID TEXT NOT NULL UNIQUE, name TEXT NOT NULL,owner_id TEXT NOT NULL, PRIMARY KEY("q_ID"))''')

#Create the access table
def access_creation(cur):
    cur.execute('''DROP TABLE IF EXISTS ACESS''')
    cur.execute('''DROP TABLE IF EXISTS ACCESS''')
    cur.execute('''CREATE TABLE ACCESS(u_ID TEXT NOT NULL, q_id TEXT NOT NULL, role TEXT NOT NULL)''')


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
def share_quiz(u_id, q_id, role):
    conn, cur = connecting_to_sql()
    cur.execute("INSERT INTO ACCESS (q_id, u_id,role) VALUES(?,?,?) ", (q_id, u_id,role))
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
        cur.execute("INSERT INTO ACCESS (q_id, u_id, role) VALUES(?,?,?) ", (q_id, u_ID, 'creator'))
    conn.commit()
    conn.close()

#return the role of a user for a specific uiz
def get_role(u_id, q_id):
    conn, cur = connecting_to_sql()
    cur.execute("SELECT role FROM ACCESS WHERE u_ID = ? AND q_ID = ?",(u_id, q_id))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0] 
    else :
        ""

def update_role(u_id, q_id, new_role):
    conn,cur = connecting_to_sql()
    cur.execute("UPDATE ACCESS SET role=? WHERE u_ID=? AND q_ID=?",(new_role, u_id, q_id))
    conn.commit()
    conn.close()
#Return whether or not a User has access to a quiz or not
def has_access(u_ID, q_ID):
    conn, cur = connecting_to_sql()
    query = "SELECT * FROM ACCESS WHERE q_ID = ? AND u_ID = ?"
    cur.execute(query,(q_ID, u_ID))
    row = cur.fetchone()
    conn.close()
    return row

def user_with_access(q_id):
    conn, cur = connecting_to_sql()
    query = "SELECT * FROM ACCESS WHERE q_ID = ?"
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
    cur.execute("DELETE FROM ACCESS WHERE u_ID = ? AND q_ID = ?", (u_id, q_id))
    conn.commit()
    conn.close()

def delete_quiz(q_id):
    conn,cur = connecting_to_sql()
    cur.execute("DELETE FROM ACCESS WHERE q_id = ?", (q_id,))
    cur.execute("DELETE FROM QUIZ WHERE q_id = ?" ,(q_id,))
    conn.commit()
    cur.execute("SELECT * FROM ACCESS WHERE q_id = ? ", (q_id,))
    test1 = cur.fetchall()
    cur.execute("SELECT * FROM QUIZ WHERE q_id = ? ", (q_id,))
    test2 = cur.fetchall()
    conn.close()
    if not (test1 and test2):
        return True
    else:
        return False
    

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
    cur.execute("INSERT INTO QUIZ (q_ID, name, owner_id) VALUES (?,?,?)", ("5d8256bb-d74c-46a6-9c97-30145f95b580", "Carrer Quiz 1", id_1))
    conn.commit()
    access_creation(cur)
    cur.execute("INSERT INTO ACCESS (u_ID, q_ID,role) VALUES (?,?,?)", (id_1, q_id_1, ROLE_CREATOR))
    cur.execute("INSERT INTO ACCESS (u_ID, q_ID,role) VALUES (?,?,?)", (id_2, q_id_1, ROLE_READER))
    cur.execute("INSERT INTO ACCESS (u_ID, q_ID,role) VALUES (?,?,?)", (id_2, q_id_2, ROLE_CREATOR))
    cur.execute("INSERT INTO ACCESS (u_ID, q_ID,role) VALUES (?,?,?)", (id_1,"5d8256bb-d74c-46a6-9c97-30145f95b580", ROLE_CREATOR))
    cur.execute("INSERT INTO ACCESS (u_ID, q_ID,role) VALUES (?,?,?)", (id_2,"5d8256bb-d74c-46a6-9c97-30145f95b580", ROLE_ADMIN))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()
