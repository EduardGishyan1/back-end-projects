"""Router for users registration and login"""

import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import APIRouter,Depends,HTTPException
from models import schemas
from utils import auth_utils
from db import db_commands,db_connection

load_dotenv()

HASHING_ALFORITHM = os.getenv("HASHING_ALGORITHM")

pwd = CryptContext(schemes= ["bcrypt"], deprecated="auto")

auth_router = APIRouter(prefix = "/auth",tags = ["Users"])

@auth_router.post("/register")
async def register_user(user:schemas.User,db = Depends(db_connection.get_db)):
    """User Registration"""
    existing_user = await db.fetchrow(db_commands.SELECT_USER_BY_USERNAME,user.username)
    if existing_user:
        raise HTTPException(status_code = 400,detail = {"messahe":"User already exists"})
    existing_email = await db.fetchrow(db_commands.SELECT_USER_BY_EMAIL,user.email)
    if existing_email:
        raise HTTPException(status_code = 400,detail = {"messahe":"Email already exists"})

    hashed_password = pwd.hash(user.password)
    await db.fetchrow(db_commands.INSERT_INTO_USERS,user.username,hashed_password,user.email)
    return {"message":"success"}

@auth_router.post("/login")
async def login_user(user:schemas.UserLoginRequest,db = Depends(db_connection.get_db)):
    """
    Authenticates user and returns JWT token.

    Args:
        username (str): User's username.
        password (str): User's password.
        db: Database connection.

    Returns:
        dict: JWT token.
    """
    user_datas = await db.fetchrow(db_commands.SELECT_USER_BY_USERNAME,user.username)
    if user_datas is None:
        raise HTTPException(status_code = 401,detail = {"message":"invalid credentials"})
   
    hashed_password =  dict(user_datas).get("password")
    if not pwd.verify(user.password,hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

            
    token = auth_utils.create_jwt_token({"username":user.username})
    return {"access_token": token, "token_type": "bearer"}

        
