"""
This program utilizes the argon2id hashing algorithm along with prehash salting and posthash peppering
to securely prepare and check passwords that are created by the user and stored in a database for use, 
this program first recieves the password from the user, applies a generated randomized salt to make brute force
GPU hash reconstrucion more difficult, and a pepper which makes it more difficult to break passwords in case
of a database breach. It then gets hashed using the argon2id algorithm into a hex string which will be stored alongside
the salt for that hex string in the database. 
"""
from pyargon2 import hash
from dataclasses import dataclass
import secrets
import dotenv
import string

   
# TODO: possible concern, not sure what information we will need to include/require for using an apache2 license that argon2 uses, I will look into it further 
# SECURITY SETTINGS - these are all set to standard security level, increasing will cause this program to take significantly longer
# Memory size = 2 Gib  
class SecureLogin:
    def __init__(self, password: str):
        #User.username=username
        #User.password=password
        pass

    @dataclass
    class User:
        username = ""
        email = ""
        password = ""
        def __init__(self, username, email, password):
            self.username = username
            self.email = email
            self.password=password
        
        def get_username(self):
            return self.username
        def get_email(self):
            return self.email


    MIN_MEMORY_SIZE = int(2097152)
    ITERATIONS = int(4)
    PARALLELISM = int(1)
    STRING_LEN = int(8)
    #TODO: PUT THIS IN A DOTENV HIDE IT DO NOT STORE IN PLANTEXT THIS IS A GLOBAL VALUE THAT WILL BE BOUNDED TO ALL PASSWORDS
    #*******************************************************
    PEPPER_STRING = "hello whatever"
    #*******************************************************
    #TODO: UPDATE A SYSTEM FOR FETCHING USERNAME
    username = "hello"
    """Password checking and salting happens here, any poorly typed password will give an error here"""
   
    def _gen_password(self)-> tuple[bool, str, str]:
        err_string = ""  
        if self._pre_hash_check()[0]:
            sp, salt = self._salt_password()
            return (True, sp, salt)
        else:
            err_string = self._pre_hash_check()[1]
            return (False, "Error Incorrect Password Formatting", err_string)

    def _hash_password(self) -> tuple[str, str]: 
        do_pepper = True 
        can_hash, primary, secondary = self._gen_password()
        if can_hash:
            if do_pepper:
                peppered_password = self._pepper_password((primary, secondary), self.PEPPER_STRING)
                return (hash(peppered_password[0], peppered_password[1], 
                            memory_cost=self.MIN_MEMORY_SIZE, 
                            time_cost=self.ITERATIONS, 
                            parallelism=self.PARALLELISM, 
                            variant='id'), secondary)
            else:
                return (hash(primary, secondary,
                            memory_cost=self.MIN_MEMORY_SIZE, 
                            time_cost=self.ITERATIONS, 
                            parallelism=self.PARALLELISM, 
                            variant='id'), secondary)
        else:
            return (primary, secondary)
    

    def check_password(self, user_password: str,db_hash: str,  db_salt: str)-> bool:
        if hash(user_password+db_salt+self.PEPPER_STRING, db_salt, 
                memory_cost=self.MIN_MEMORY_SIZE, 
                time_cost=self.ITERATIONS, 
                parallelism=self.PARALLELISM, 
                variant='id') == db_hash:
            return True
        return False
                
#HELPERS
    
    
    def _gen_random_salt_string(self, length : int)-> str:
        alphabet = string.ascii_letters+string.digits
        curr_salt = ''.join(secrets.choice(alphabet) for _ in range(length))
        return curr_salt
    
    def _special_char_check(self, password)-> bool:
        SPECIAL_CHARACTERS = "!@#$%&?"
        for character in SPECIAL_CHARACTERS: 
            if character in password:
                return True
        return False

    def _salt_password(self) -> tuple[str, str]:
        salt = self._gen_random_salt_string(self.STRING_LEN) 
        return (password+salt, salt) 

    def _pepper_password(self, salted_pass: tuple[str,str], pepper: str)-> tuple[str,str]:
            return(salted_pass[0] + pepper, salted_pass[1])

    def _pre_hash_check(self)-> tuple[bool, str]:
            if len(password) < 8:
                err_string = "Error: Password too short"
                return (False, err_string)
            elif self.username in password:
                err_string = "Error: Username can not be contained within password"
                return (False, err_string)
            elif len(password) >= 129:
                err_string = "Error: Password too long"
                return (False, err_string)
            elif not self._special_char_check(password):
                err_string = "Error: Password must contain one of the following !, @, #, $, %, &, ?"
                return (False, err_string)
            else:
                return (True, "")

# PUBLIC METHODS
    def fetch_data_to_compare(self):
        pass
    def password_creation_send(self):
        return self._hash_password()
        
        




if __name__ == "__main__": 
    password = input("Enter a Password for encryption: ")
    login = SecureLogin(password)
    output = login.password_creation_send()
    print(output)
    if login.check_password(password, output[0], output[1]):
        print("passed")
    else:
        print("no match")




    
 
