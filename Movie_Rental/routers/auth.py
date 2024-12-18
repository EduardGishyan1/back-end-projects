from fastapi import APIRouter,HTTPException
from models import schemas
import aiofiles
import json

users_file = "users.json"

users = {}

users_router = APIRouter(prefix = "/auth")

async def write_users_file(data):
    with aiofiles.open(users_file) as fs:
        await json.dumps(data,users_file,indent=2)

async def read_users_file():
    with aiofiles.open(users_file) as fs:
        return await json.load(fs)

@users_router.post("/register")
async def register_user(user:schemas.User):
        users_list = await read_users_file()
        for user_data in users_list:
            if user_data.get("username") == user.get("username"):
                raise HTTPException(status_code = 400,detail = {"message":"user already exists"})
        users[user.get("username")] = user
        await write_users_file(users)
    
@users_router.post("/login")
async def login_user(username,password):
    user_datas = await read_users_file()
    for user_data in user_datas:
        if user_data.username == username and user_data.password == password:
            pass