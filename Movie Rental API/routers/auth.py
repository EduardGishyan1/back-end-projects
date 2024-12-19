"""Router for users registration and login"""

import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import APIRouter,Depends,Form,HTTPException
from utils import auth_utils
from db import db_commands,db_connection

load_dotenv()

HASHING_ALFORITHM = os.getenv("HASHING_ALGORITHM")

pwd = CryptContext(schemes="sha256_crypt")

auth_router = APIRouter(prefix = "/auth",tags = ["Users"])

@auth_router.post("/register")
async def register_user(username=Form(...),password=Form(...),email=Form(...),db = Depends(db_connection.get_db)):
    """User Registration"""
    existing_user = await db.fetchrow(db_commands.SELECT_USER_BY_USERNAME,username)
    if existing_user:
        raise HTTPException(status_code = 400,detail = {"messahe":"User already exists"})
    existing_email = await db.fetchrow(db_commands.SELECT_USER_BY_EMAIL,email)
    if existing_email:
        raise HTTPException(status_code = 400,detail = {"messahe":"Email already exists"})

    hashed_password = pwd.hash(password)
    await db.fetchrow(db_commands.INSERT_INTO_USERS,username,hashed_password,email)

@auth_router.post("/login")
async def login_user(username = Form(...),password = Form(...),db = Depends(db_connection.get_db)):
    """
    Authenticates user and returns JWT token.

    Args:
        username (str): User's username.
        password (str): User's password.
        db: Database connection.

    Returns:
        dict: JWT token.
    """
    
    user_datas = await db.fetchrow(db_commands.SELECT_USER_BY_USERNAME,username)
    user_password = dict(user_datas).get("password")
    if pwd.verify(password,user_password):
        token = auth_utils.create_jwt_token({"username":username})
        return {"token":token}
