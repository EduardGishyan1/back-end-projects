from passlib.context import CryptContext
from users_db import verify_password,hash_password
from users_db import UserDB


pwd = CryptContext(schemes="sha256_crypt")


def register_user(username:str,password:str):
    if UserDB().get_user(username):
        return False
    hashed_password = hash_password(password)
    UserDB().add_user(username,hashed_password)
    return {"username":username}
    
def login_user(username:str,password:str):
    user = UserDB().get_user(username)
    if not user:
        return False
    return verify_password(password,user["password"])


