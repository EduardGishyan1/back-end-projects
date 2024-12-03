from fastapi import FastAPI,HTTPException,Request
import uvicorn
import json
import os
import aiofiles
from dotenv import load_dotenv
from errors import ValidationError,FileError,NotFoundError
from pydantic import BaseModel
from typing import Optional

load_dotenv()

if os.path.exists(".env"):
    USERS_FILE = os.getenv("USERS_FILE")
    TASKS_FILE = os.getenv("TASKS_FILE")
    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))

class User(BaseModel):
    name:str
    email:str
    password:str
    
class Task(BaseModel):
    user_id:int
    title:str
    description:Optional[str]


app = FastAPI()


async def read_json_file(file_path:str):
    try:
        async with aiofiles.open(file_path,mode="r") as fs:
            content = await fs.read()
            return json.loads(content) if content else []
        
    except FileNotFoundError:
        raise FileError(detail="File not found or invalid json format")
    
    except Exception as e:
        raise HTTPException(status_code = 400,detail = str(e))
    
async def write_json_file(file_path:str,data:dict)->None:
    try:
        async with aiofiles.open(file_path,mode="w") as fs:
            await fs.write(json.dumps(data,indent=2))
    
    except FileNotFoundError:
        raise FileError(detail="File not found or invalid json format")
    
    except json.JSONDecodeError:
        raise FileError(detail="File not found or invalid json format")
            
    except Exception as e:
        raise HTTPException(status_code = 400,detail = f"Error:{str(e)}")        

async def userid_validate(user_id:int):
    if user_id == None:
            raise ValidationError(detail="user id must refer to an existing user.")
    users = await read_json_file(USERS_FILE)
    if not any(user["id"] == user_id for user in users):
        raise ValidationError(detail="user id must refer to an existing user.")

async def email_unique(email: str):
    users = await read_json_file(USERS_FILE)
    if any(user["email"] == email for user in users):
        raise ValidationError(detail="Email already registered.")
    
async def delete_item_by_id(file_path:str,item_id:int):
    content = await read_json_file(file_path)
    if content:
        for item in content:
            if item.get("id") == item_id:
                content.remove(item)
                await write_json_file(file_path,content)
                return {"message":"success"}
            
        raise NotFoundError()
    raise NotFoundError()
   
@app.get("/users")
async def get_users():
        users = await read_json_file(USERS_FILE)
        return users

@app.get("/tasks")
async def get_tasks():
        tasks = await read_json_file(TASKS_FILE)
        return tasks  

@app.get("/users/{u_id}")
async def get_user_byid(u_id:int):
    users:list[dict] = await read_json_file(USERS_FILE)
    for user in users:
        if user["id"] == u_id:
            return user
    
    raise NotFoundError()
       
@app.get("/tasks/{t_id}")
async def get_task_byid(t_id:int):
    try:    
        tasks = await read_json_file(TASKS_FILE)
        
        for task in tasks:
            if task["id"] == t_id:
                return task
            
        raise NotFoundError(detail = "task not found")

    except Exception as e:
        raise HTTPException(status_code = 400,detail = str(e))
        
        
@app.post("/register")
async def register(user:User)->dict:
    try:
        user = user.dict()
        await email_unique(user["email"])
        users = await read_json_file(USERS_FILE)
        max_id = max([user["id"] for user in users],default=0)
        user["id"] = max_id+1
        users.append(user)
        
        await write_json_file(USERS_FILE,users)
        return user

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/login")
async def login(datas:User):
    try:
        users = await read_json_file(USERS_FILE)
        datas = datas.dict()
        if users:
            for user in users:
                if user.get("email") == datas.get("email") and user.get("password") == datas.get("password"):
                    return {"message":"login successfully"}
            raise NotFoundError()
        else:
            raise NotFoundError()
    
    except Exception as e:
        raise HTTPException(status_code = 400,detail = str(e))

@app.put("/users/{user_id}")
async def update_user(user_id:int,request:Request):
    try:
        user = await request.json()
        users = await read_json_file(USERS_FILE)
        index = next((i for i,j in enumerate(users) if j["id"] == user_id),None)
        if index == None:
            raise NotFoundError(detail="User not found")
        users[index] = {**users[index], **user}
        await write_json_file(USERS_FILE,users)
        return users[index]
    except Exception as e:
        raise HTTPException(status_code = 400,detail = str(e))

@app.post("/post_task")
async def add_task(task:Task)-> dict:
    try:
        task = task.dict()
        userid_validate(task["user_id"])
        content = await read_json_file(TASKS_FILE)
        
        tasks = content if content else []
        max_id = max([task["id"] for task in tasks],default=0)
        task["id"] = max_id+1
        tasks.append(task)
        
        await write_json_file(TASKS_FILE,tasks)
        return task

    except Exception as e:
        raise HTTPException(status_code = 400,detail = str(e))

        
@app.delete("/del_user/{id}")
async def del_user(id:int):
    await delete_item_by_id(USERS_FILE,id)
    
@app.delete("/del_task/{id}")
async def del_task(id:int):
    await delete_item_by_id(TASKS_FILE,id)

    
if __name__ == "__main__":
    print(f"server is running on {host}:{port} ")
    uvicorn.run("main:app",host = host,port = port,reload=True)