import json
from passlib.context import CryptContext
import os

pwd = CryptContext(schemes="sha256_crypt")

class UserNotFound(Exception):
    pass

class UserDB:
    def __init__(self,db_file = "users.json"):
        self.db_file = db_file
        self.load_data()
        
    def load_data(self):
        if os.path.exists(self.db_file):
            with open(self.db_file,mode="r") as file:
                self.users = json.loads(file.read())
        
        else:
            self.users = {}
            
    def save_data(self):
        with open(self.db_file,mode="w") as fs:
            json.dump(self.users,fs,indent=2)
    
    def get_user(self,username:str):
        if self.users:
            return self.users.get(username)
        return False
    
    def add_user(self,username:str,password:str):
        self.users[username] = {"username":username,"password":password}
        self.save_data()
        

def hash_password(password:str):
    return pwd.hash(password)

def verify_password(hashed_password,password:str):
    return pwd.verify(hashed_password,password)
    