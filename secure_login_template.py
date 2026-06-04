"""
This program utilizes the argon2id hashing algorithm along with prehash salting and posthash peppering
to securely prepare and check passwords that are created by the user and stored in a database for use, 
this program first recieves the password from the user, applies a generated randomized salt to make brute force
GPU hash reconstrucion more difficult, and a pepper which makes it more difficult to break passwords in case
of a database breach. It then gets hashed using the argon2id algorithm into a hex string which will be stored alongside
the salt for that hex string in the database. 
"""
# TODO: possible concern, not sure what information we will need to include/require for using an apache2 license that argon2 uses, I will look into it further 
# SECURITY SETTINGS - these are all set to standard security level, increasing will cause this program to take significantly longer
# Memory size = 2 Gib 
MIN_MEMORY_SIZE = 2097152
ITERATIONS = 4
PARALLELISM = 1

STRING_LEN = 8
#TODO: PUT THIS IN A DOTENV HIDE IT DO NOT STORE IN PLANTEXT THIS IS A GLOBAL VALUE THAT WILL BE BOUNDED TO ALL PASSWORDS
PEPPER_STRING = "hello whatever"
from pyargon2 import hash
import secrets
import dotenv
import string
username = "hello"
"""Password checking and salting happens here, any poorly typed password will give an error here"""
def gen_password(password: str)-> tuple[str, str]:
    err_string = "" 

    def salt_password(password : str) -> tuple[str, str]:
        salt = gen_random_salt_string(STRING_LEN) 
        return (password+salt, salt)

    def pre_hash_check(password:str )-> bool | tuple[bool, str]:
        if len(password) < 8:
            err_string = "Error: Password too short"
            return (False, err_string)
        elif username in password:
            err_string = "Error: Username can not be contained within password"
            return (False, err_string)
        elif len(password) >= 129:
            err_string = "Error: Password too long"
            return (False, err_string)
        else:
            return True
   
    if type(pre_hash_check(password)) == bool and pre_hash_check(password):
        return salt_password(password)
    else:
        return ("Error Incorrect Password Formatting", err_string)
    
def hash_password(password: tuple[str,str]) -> str: 
    do_pepper = True 
    def pepper_password(salted_pass: tuple[str,str], pepper: str)-> tuple[str,str]:
        return(salted_pass[0] + pepper, salted_pass[1])
    if do_pepper:
        peppered_password = pepper_password(password, PEPPER_STRING)
        return hash(peppered_password[0], peppered_password[1], memory_cost=MIN_MEMORY_SIZE, time_cost=ITERATIONS, parallelism=PARALLELISM, variant='id')
    else:
        return hash(password[0], password[1] ,memory_cost=MIN_MEMORY_SIZE, time_cost=ITERATIONS, parallelism=PARALLELISM, variant='id')
    

                       
    

def check_password(user_password: str,db_hash: str,  db_salt: str)-> bool:
    if hash(user_password+db_salt+PEPPER_STRING, db_salt, memory_cost=MIN_MEMORY_SIZE, time_cost=ITERATIONS, parallelism=PARALLELISM, variant='id') == db_hash:
        return True
    return False
    
# HELPERS
def gen_random_salt_string(length : int)-> str:
    alphabet = string.ascii_letters+string.digits
    curr_salt = ''.join(secrets.choice(alphabet) for _ in range(length))
    return curr_salt

if __name__ == "__main__": 
    password = input("Enter a Password for encryption: ")
    
    prepped_password = gen_password(password)
    print(prepped_password)
    hashed_password = hash_password(prepped_password)
    print(hashed_password)

    
 
