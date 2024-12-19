"""Helper functions for JWT token creation and validation"""

import os
import datetime
from jose import jwt,JWTError
from dotenv import load_dotenv
from fastapi import Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "auth/login")

SECRET_KEY = os.getenv("SECRET_KEY")
EXPIRES_IN = int(os.getenv("EXPIRES_IN"))
HASHING_ALGORITHM = os.getenv("HASHING_ALGORITHM", "HS256")

def create_jwt_token(data):
    """Create JWT Token"""
    expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=EXPIRES_IN)
    users = data.copy()
    users["exp"] = expires
    return jwt.encode(claims=users, key=SECRET_KEY, algorithm=HASHING_ALGORITHM)

def verify_token(token: str):
    """
    Validates JWT token and returns the username.

    Args:
        token (str): JWT token.

    Returns:
        str: Decoded username.
    """    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[HASHING_ALGORITHM])
        return payload.get("sub")  
    except JWTError:
        return None
   
def get_current_user(token:str = Depends(oauth2_scheme)):
    """Get current user"""
    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code = 400,detail = "Inavlid token")
    return username
