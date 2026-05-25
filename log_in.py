#TODO WILL HAVE TO CREATE A LOG IN SYSTEM THAT IS SECURE --> HASH TABLE AND THE SUCH --> FOR NOW WE"LL JUST BE STORING AND RETRIEVING THING IN THE DB AS PLAINTEXT
# when we have the server we'll switch to hashtable (or before maybe)
import sqlite3
import uuid



#As it stand you cannot carry sql statement between python file, therefore it will allow us to connect to the DB
def connecting_to_sql():
    conn = sqlite3.connect("carrer_quiz.db")
    cur = conn.cursor()
    return conn,cur

#Log in a User into the System
#TODO as mentioned in the header, has it stand it's very unsafe (storing info in plain text). We need to change this and use a hash table
def login_user(username, password):
    conn, cur = connecting_to_sql()
    query = """
    SELECT * FROM USER WHERE Username = ?;
    """
    cur.execute(query, (username,))
    user = cur.fetchone()
    if(not user):
        conn.close()
        return -1
    
    query = """
    SELECT * FROM USER WHERE Username = ?
    AND Password = ?;
    """

    cur.execute(query, (username, password))
    user = cur.fetchone()
    if (not user):
        conn.close()
        return -2
    else:
        conn.close()
        return user[0]
    
#Register a user into the system.
#TODO same as the above function
def registering_user(username,password,email):
    conn, cur = connecting_to_sql()
    query = """
            SELECT * FROM USER WHERE Username = ?
            """
    cur.execute(query, (username,))
    user = cur.fetchone()
    if (user):
        conn.close()
        return -1
    else :
        query = """
            SELECT * FROM USER WHERE email = ?
            """
        cur.execute(query, (email,))
        user = cur.fetchone()
        if (user):
            conn.close()
            return -2
        user = True
        while(user):
            id = str(uuid.uuid4())
            query = """
                SELECT * FROM USER WHERE u_id = ?
                """
            cur.execute(query, (username,))
            user = cur.fetchone()
        query = """ 
            INSERT INTO USER (u_ID,Username, Password, Email) VALUES (?,?,?,?);
        """
        cur.execute(query, (id,username,password, email))
        conn.commit()
        conn.close()
        return id
