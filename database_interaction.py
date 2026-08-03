"""
Create the database. Allow manipulation to the DB too.  
WARNING : CALLING CREATE_DB() WILL ESENTIALLY WIPE ALL DATA.
To be used by an admin to wipe all data
"""

import sqlite3
from sqlite3 import Connection, Cursor
import response_table_interaction as rti

ROLE_CREATOR = "creator"
ROLE_ADMIN   = "admin"
ROLE_EDITOR  = "editor"
ROLE_READER  = "reader"
ROLE_RANK = { ROLE_CREATOR:4, 
              ROLE_ADMIN:3, 
              ROLE_EDITOR:2, 
              ROLE_READER:1 }


def connecting_to_sql() -> tuple[Connection, Cursor]:
    """
    As it stand you cannot carry sql statement between python file, therefore this function allow us to connect to the database

    Returns:
        tupple : a tupple containing the connection to the database, and the cursor to said database
    """
    conn = sqlite3.connect("career_quiz.db") 
    cur = conn.cursor()
    return conn,cur

def can_edit(role : str) -> bool:
    """
    Allow us to know if a user can edit a quiz

    Args:
        role(str): the role of the user
    Returns:
        boolean : whether the role is creator, admin, or editor.
    """
    return role in (ROLE_CREATOR, ROLE_ADMIN, ROLE_EDITOR)

def can_share(role: str) -> bool: 
    """
    Allow us to know if a user can share a quiz
    Args:
        role(str) : the role of the user
    Returns:
        boolean : whether the role is creator, or admin
    """
    return role in (ROLE_CREATOR, ROLE_ADMIN)

def can_assign(role: str) -> bool:
    """
    Allow us to know if a user can assign a quiz
    Args:
        role(str): the role of the user
    Returns:
        boolean : whether the role is creator, admin, or editor.
    """
    return role in (ROLE_CREATOR, ROLE_ADMIN, ROLE_EDITOR)

def can_delete(role: str) -> bool: 
    """
    Allow us to know if a user can delete a quiz
    Args:
        role(str) : the role of the user
    Returns:
        boolean : whether the role is the creator or not 
    """
    return role == ROLE_CREATOR

def can_revoke(role: str) -> bool: 
    """
    Allow us to know if a user can revoke access to a quiz
    Args:
        role(str) : the role of the user
    Returns:
        boolean : whether the role is creator, or admin
    """
    return role in (ROLE_CREATOR, ROLE_ADMIN)

def can_promote(actor_role: str , target_role : str) -> bool:
    """
    Allow us to know if a user can promote another user

    Args:
        actor_role(str) : the role of the user that try to promote
        target_role (str): the role of the promoted user

    Returns:
        boolean : whether the promoter try to promote above his station or not
    """
    if target_role == ROLE_CREATOR: 
        return False
    return ROLE_RANK.get(actor_role,0) > ROLE_RANK.get(target_role,0)
    
def user_creation(cur : Cursor):
    """
    Create the user table

    Args:
        cur(Cursor) : a cursor to the database 
    """
    cur.execute('''DROP TABLE IF EXISTS USER''')
    cur.execute('''CREATE TABLE USER(u_ID TEXT NOT NULL UNIQUE, Username TEXT NOT NULL UNIQUE , Password TEXT NOT NULL, Email TEXT NOT NULL UNIQUE, PRIMARY KEY("u_ID"))''')


def quiz_creation(cur:Cursor):
    """
    Create the quiz table

    Args:
        cur(Cursor) : a cursor to the database 
    """
    cur.execute('''DROP TABLE IF EXISTS QUIZ''')
    cur.execute('''CREATE TABLE QUIZ(q_ID TEXT NOT NULL UNIQUE, name TEXT NOT NULL,owner_id TEXT NOT NULL, PRIMARY KEY("q_ID"))''')


def access_creation(cur:Cursor):
    """
    Create the access table

    Args:
        cur(Cursor) : a cursor to the database 
    """
    cur.execute('''DROP TABLE IF EXISTS ACESS''')
    cur.execute('''DROP TABLE IF EXISTS ACCESS''')
    cur.execute('''CREATE TABLE ACCESS(u_ID TEXT NOT NULL, q_id TEXT NOT NULL, role TEXT NOT NULL)''')


def user_responses(cur : Cursor):
    """
    We have to create a table that stores quiz responses on quiz id's for users in USERS
    Create the user_response table, that store if user completed quiz, as well as a key to a json that contain their answer

    Args:
        cur(Cursor) : a cursor to the database 
    """
    cur.execute('''DROP TABLE IF EXISTS USER_RESPONSES''')
    cur.execute('''CREATE TABLE  USER_RESPONSES(u_ID TEXT NOT NULL UNIQUE, num_completed_quizzes int ,quizzes_assigned TEXT, quizzes_completed TEXT, quiz_response_answers TEXT)''')



def find_name_with_id(q_id : str) -> str | None:
    """
    find the name of a QUIZ with it's id

    Args:
        q_id(str) : the id of the quiz which we're trying to find a name for 
    """
    conn, cur = connecting_to_sql()
    query = "SELECT name FROM QUIZ WHERE q_ID = ?"
    cur.execute(query,(q_id,))
    row = cur.fetchall()

    conn.close()
    if row : 
        return row[0][0]
    else :
        return None

#TODO this comment can be generalized but I think we should look into strong typing the ret on these functions, unions with none may be a little weak as we might be passing a value when it should throw
def find_id_with_uname(username: str) -> str: # was str | None
    """
    find the id of a USER with it's username

    Args:
        username(str) : the name of the user who's id we're trying to find 
    """
    conn, cur = connecting_to_sql()
    query = "SELECT u_id FROM USER WHERE Username = ?"

    cur.execute(query,(username,))

    row = cur.fetchone()

    conn.close()

    if row :
        return row[0]
    else :
        raise sqlite3.Error


def find_uname_with_id(u_id :str ) -> str | None :
    """
    find the name of a USER with it's id

    Args:
        u_id(str) : the id of the user who's name we're trying to find 
    """
    conn, cur = connecting_to_sql()
    cur.execute("SELECT Username FROM USER WHERE u_ID = ?", (u_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None


def share_quiz(u_id : str , q_id : str, role : str):
    """
    allow for sharing of a quiz with someone else

    Args:
        u_id(str) : the id of the user who's being given access to the quiz
        q_id(str) : the id of the quiz who's being shared 
        role (str) : the role that is being given to the user
    """

    conn, cur = connecting_to_sql()
    cur.execute("INSERT INTO ACCESS (q_id, u_id,role) VALUES(?,?,?) ", (q_id, u_id,role))
    conn.commit()
    conn.close()

    # must run on its own connection AFTER the commit above, an open write
    # transaction here locks the db out from under USER_RESPONSES
    if role == ROLE_READER:
        rti.user_assigned_new_quiz(u_id, q_id)


def save_quiz_in_the_db(q_id : str, q_title : str , u_ID :str ):
    """
    allow for saving a quiz
    If the quiz already exist it simply update it, otherwise it create a new row in the db

    Args:
        q_id(str) : the id of the quiz (given before we arrive to this step)
        q_title(str) : the title of the quiz  
        u_id (str) : the id of the person who's saving the quiz.
    """
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


def get_role(u_id : str, q_id : str) -> str | None:
    """
    Get the role of a user for a specific quiz.

    Args:
        u_id (str): the id of the user to get the role for
        q_id (str): the id of the quiz to get the role for

    Returns:
        str | None: the role of the user, or None if the user does not have a role for this quiz.
    """
    conn, cur = connecting_to_sql()
    cur.execute("SELECT role FROM ACCESS WHERE u_ID = ? AND q_ID = ?",(u_id, q_id))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0] 
    else :
        return None

def update_role(u_id : str, q_id : str, new_role: str):
    """
    update the role of a user for a specific quiz.

    Args:
        u_id(str): the id of the user who's role is update
        q_id(str): the id of the quiz
        new_role(str) : the new role given to the user
    """
    conn,cur = connecting_to_sql()
    cur.execute("UPDATE ACCESS SET role=? WHERE u_ID=? AND q_ID=?",(new_role, u_id, q_id))
    conn.commit()
    conn.close()


def has_access(u_ID: str , q_ID : str) -> bool:
    """
    Return whether or not a User has access to a quiz or not
    Args:
        u_id (str): the id of the user who we're checking
        q_id (str): the id of the quiz to check

    Returns:
        bool : whether or not a user has access to a quiz or not
    """
    conn, cur = connecting_to_sql()
    query = "SELECT * FROM ACCESS WHERE q_ID = ? AND u_ID = ?"
    cur.execute(query,(q_ID, u_ID))
    row = cur.fetchone()
    conn.close()
    return row

def user_with_access(q_id : str) -> list[str] | None:
    """
    Return the users who have acess to the quiz
    Args:
        q_id (str): the id of the quiz to check

    Returns:
        list[str] : a list containing all information about a quiz
    """
    conn, cur = connecting_to_sql()
    query = "SELECT * FROM ACCESS WHERE q_ID = ?"
    cur.execute(query,(q_id,))
    row = cur.fetchall()
    conn.close()
    if row:   
        return row
    else: 
        return None


def quizzes_for_user(u_id : str):
    """
    Retrieve all quizzes that a user has access to.

    Args:
        u_id (str): the id of the user whose quizzes we want to retrieve

    Returns:
        list: a list of dictionaries, each containing the quiz id and name
              of a quiz the user has access to. Returns an empty list if
              the user has no quizzes.
    """
    conn, cur = connecting_to_sql()
    query = """
        SELECT QUIZ.q_ID, QUIZ.name
        FROM ACCESS
        JOIN QUIZ ON ACCESS.q_ID = QUIZ.q_ID
        WHERE ACCESS.u_ID = ?
    """
    cur.execute(query, (u_id,))
    rows = cur.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1] or None} for row in rows]



def find_creator(q_id : str) -> str | None:
    """
    find the creator of a quiz

    Args:
        q_id (str): the id of the quiz whose creator we want to find

    Returns:
        str | None : either the name of the creator, or None if a quiz has no creator (doesnt exist)
    """
    conn, cur = connecting_to_sql()
    cur.execute("SELECT Username FROM USER JOIN QUIZ ON USER.u_ID = QUIZ.owner_id WHERE QUIZ.q_ID = ?", (q_id,))
    row = cur.fetchone()
    conn.close()
    if row :
        return row[0]
    else :
        return None


def remove_access(u_id : str, q_id : str):
    """
    remove the acces of a user to a quiz

    Args:
        u_id (str) : the id of the user who's being removed from the quiz
        q_id (str): the id of the quiz whose permission we're changing

    """
    conn, cur = connecting_to_sql()
    cur.execute("DELETE FROM ACCESS WHERE u_ID = ? AND q_ID = ?", (u_id, q_id))
    conn.commit()
    conn.close()

def delete_quiz(q_id: str) -> bool:
    """
    fully delete a quiz from the database. The file itself is deleted upstream

    Args:
        q_id (str): the id of the quiz that is being deleted
    Returns:
        bool : whether it was truly removed from the db or not
    """
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
    

def create_db():
    """
    Call the first 4 function in the database_interaction.py file to create the Database.
    CAUTION : CALLING IT CAUSE A MASSIVE WIPE OF EVERY DATA CONTAINED IN THE DATABASE
    """
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
    cur.execute("INSERT INTO QUIZ (q_ID, name, owner_id) VALUES (?,?,?)", ("5d8256bb-d74c-46a6-9c97-30145f95b580", "Career Quiz 1", id_1))
    conn.commit()
    access_creation(cur)
    cur.execute("INSERT INTO ACCESS (u_ID, q_ID,role) VALUES (?,?,?)", (id_1, q_id_1, ROLE_CREATOR))
    cur.execute("INSERT INTO ACCESS (u_ID, q_ID,role) VALUES (?,?,?)", (id_2, q_id_1, ROLE_READER))
    cur.execute("INSERT INTO ACCESS (u_ID, q_ID,role) VALUES (?,?,?)", (id_2, q_id_2, ROLE_CREATOR))
    cur.execute("INSERT INTO ACCESS (u_ID, q_ID,role) VALUES (?,?,?)", (id_1,"5d8256bb-d74c-46a6-9c97-30145f95b580", ROLE_CREATOR))
    cur.execute("INSERT INTO ACCESS (u_ID, q_ID,role) VALUES (?,?,?)", (id_2,"5d8256bb-d74c-46a6-9c97-30145f95b580", ROLE_ADMIN))
    conn.commit()
    user_responses(cur)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()
