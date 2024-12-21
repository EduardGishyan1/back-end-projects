"""Helper functions for JWT token creation and validation"""

import os
import datetime
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
EXPIRES_IN = int(os.getenv("EXPIRES_IN"))
HASHING_ALGORITHM = os.getenv("HASHING_ALGORITHM", "HS256")

def create_jwt_token(data):
    """Create JWT Token"""
    expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=EXPIRES_IN)
    users = data.copy()
    users["exp"] = expires
    return jwt.encode(claims=users, key=SECRET_KEY, algorithm=HASHING_ALGORITHM)

