from fastapi import FastAPI,HTTPException,Request
import uvicorn
import json
import os
import aiofiles
from dotenv import load_dotenv
import re
from errors import ValidationError,FileError,NotFoundError


load_dotenv()
users_file = os.getenv("USERS_FILE")
tasks_file = os.getenv("TASKS_FILE")
host = os.getenv("HOST")
port = int(os.getenv("PORT"))


app = FastAPI()


async def read_json_file(file_path:str):
    try:
        async with aiofiles.open(file_path,mode="r") as fs:
            content = await fs.read()
            return json.loads(content) if content else []
        
    except (FileNotFoundError,json.JSONDecodeError):
        raise FileError("File not found or invalid json format")
    
async def write_json_file(file_path:str,data:dict)->None:
    try:
        async with aiofiles.open(file_path,mode="w") as fs:
            await fs.write(json.dumps(data,indent=2))
            
    except Exception as e:
        raise FileError(f"Error:{str(e)}")        
    
async def email_validate(email):
        valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',email)
        if not valid:
            raise ValidationError("Enter valid email address...")
        return "success"
        
async def password_validate(password):
    required_characters = 6
    if len(password) < required_characters:
        raise ValidationError(f"length of password must be greather or equal then {required_characters}")
    return "success"
        

async def name_validate(name):  
    if not name or not isinstance(name,str):
        raise ValidationError("name must be non-empty string...")
    return "success"

async def userid_validate(user_id:int):
    if user_id == None:
            raise ValidationError("user id must refer to an existing user.")
    users = await read_json_file(users_file)
    for user in users:
        if user["id"] == user_id:
            return "success"
    raise ValidationError("user id must refer to an existing user.")
        

async def title_validate(title):
    if title == None:
        raise ValidationError("Title must be non-empty string")

    if not title:
        raise ValidationError("Title must be non-empty string")
    return "success"

async def description_validate(description = None):
    if description != None and not isinstance(description,str):
        raise ValidationError("Description must be string or None")
    return "success"

async def email_unique(email: str):
    users = await read_json_file(users_file)
    if any(user["email"] == email for user in users):
        raise ValidationError("Email already registered.")
   
@app.get("/users")
async def get_users():
    try:
        users_list = []
        users = await read_json_file(users_file)
            
        for user in users:
            users_list.append({"id":user["id"],"name":user["name"],"email":user["email"]})
        
        return users_list

    except Exception as e:
        raise HTTPException(status_code = 400,detail = str(e))

@app.get("/tasks")
async def get_tasks():
    try:
        tasks = await read_json_file(tasks_file)
        return tasks  
    except Exception as e:
        raise HTTPException(status_code = 400,detail = str(e))   

@app.get("/users/{u_id}")
async def get_user_byid(u_id:int):
    users:list[dict] = await read_json_file(users_file)
    for user in users:
        if user["id"] == u_id:
            user["password"] = 6 * "*"
            return user
    
    raise HTTPException(status_code = 400,detail = "Not found") 
       
@app.get("/tasks/{t_id}")
async def get_task_byid(t_id:int):
    try:    
        tasks = await read_json_file(tasks_file)
        
        for task in tasks:
            if task["id"] == t_id:
                return task
            
        raise HTTPException(status_code = 400 , detail = "task not found")

    except Exception as e:
        raise HTTPException(status_code = 400,detail = str(e))
        
        
@app.post("/register")
async def register(user:dict)->dict:
    try:
        try:
            await password_validate(user.get("password",None))
            await email_validate(user.get("email",None))
            await email_unique(user.get("email",None))
            await name_validate(user.get("name",None))
        except ValidationError as e:
            raise HTTPException(status_code = 400,detail = str(e))
        
        content = await read_json_file(users_file)
        users = content if content else []
        max_id = max([user["id"] for user in users],default=0)
        user["id"] = max_id+1
        users.append(user)
        
        await write_json_file(users_file,users)
        user.pop("password")
        return user

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/login")
async def login(datas:dict):
    try:
        users = await read_json_file(users_file)
        if users:
            for user in users:
                if user.get("email") == datas.get("email") and user.get("password") == datas.get("password"):
                    return {"message":"login successfully"}
            raise HTTPException(status_code = 400,detail = "not found")
        else:
            raise HTTPException(status_code = 400,detail = "not found")
    
    except (FileError,ValidationError,NotFoundError) as e:
        raise HTTPException(status_code = 400,detail = str(e))

@app.put("/users/{user_id}")
async def update_user(user_id:int,request:Request):
    user = await request.json()
    users = await read_json_file(users_file)
    index = next((i for i,j in enumerate(users) if j["id"] == user_id),None)
    if index == None:
        raise NotFoundError("User not found")
    users[index] = {**users[index], **user}
    await write_json_file(users_file,users)
    return users[index]
    

@app.post("/post_task")
async def add_task(task:dict)-> dict:
    try:
        try:
            await userid_validate(task.get("user_id",None))
            await description_validate(task.get("description",None))
            await title_validate(task.get("title",None))
        except ValidationError as e:
            raise HTTPException(status_code = 400,detail = str(e))
        
        content = await read_json_file(tasks_file)
        
        tasks = content if content else []
        max_id = max([task["id"] for task in tasks],default=0)
        task["id"] = max_id+1
        tasks.append(task)
        
        await write_json_file(tasks_file,tasks)
            
        return task

    except (FileError,ValidationError,NotFoundError) as e:
        raise HTTPException(status_code = 400,detail = str(e))

        
@app.delete("/del_user/{id}")
async def del_user(id:int):
    content = await read_json_file(users_file)
    flag = False
    for user in content:
        if user["id"] == id:
            flag = True
            break
                
    if flag:  
            for user in content:
                if user["id"] == id:
                    content.remove(user)
                    await write_json_file(users_file,content)
                    return {"message":"success"}

            raise HTTPException(status_code = 400,detail = "not found")
    else:
        raise HTTPException(status_code = 400,detail = "not found")
    
@app.delete("/del_task/{id}")
async def del_task(id:int):
    content = await read_json_file(tasks_file)
    flag = False
    for task in content:
        if task["id"] == id:
            flag = True
            break
                
    if flag:  
        for task in content:
            if task["id"] == id:
                content.remove(task)
                await write_json_file(tasks_file,content)
                return {"message":"success"}
            
        raise HTTPException(status_code = 400,detail = "not found")
    
    else:    
        raise HTTPException(status_code = 400,detail = "not found")
    
if __name__ == "__main__":
    print(f"server is running on {host}:{port} ")
    uvicorn.run("main:app",host = host,port = port)
