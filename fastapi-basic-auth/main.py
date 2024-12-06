from fastapi import FastAPI,Request,Form,HTTPException,Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from log_activity import log_event
from auth import register_user,login_user
import uvicorn
from auth import UserDB
from dotenv import load_dotenv
import os
import time

load_dotenv()

if os.path.exists(".env"):
    PORT = int(os.getenv("PORT"))

templates = Jinja2Templates(directory = "static/templates")
app = FastAPI()

@app.get("/")
async def login(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

@app.get("/register")
async def register(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})

@app.post("/register")
async def post_register(username:str = Form(...),password:str = Form(...)):
    if register_user(username,password) == False:
        raise HTTPException(status_code = 400,detail = "Username already exist")
    log_event("register", username, "success")
    return RedirectResponse(url = "/secure",status_code = 303)

@app.post("/")
async def post_login(username:str = Form(...),password:str = Form(...)):
    if login_user(username,password) == False:
        raise HTTPException(status_code = 400,detail = "Invalid Credentials")
    else:
        redirect_response = RedirectResponse(url = "/secure",status_code = 303)
        redirect_response.set_cookie(key="username",value = username)
        log_event("login", username, "success")
        return redirect_response

@app.get("/logout")
def logout_user():
    """
    Logs out the user by deleting the session cookie and redirecting to the login page.
    """
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("username")

    return response
    
@app.get("/secure")
async def secure_page(request:Request):
    username = request.cookies.get("username")
    if not username or not UserDB().get_user(username):
        return RedirectResponse(url = "/",status_code = 303)
    return templates.TemplateResponse("secure.html",{"request":request,"username":username})

if __name__ == "__main__":
    uvicorn.run("main:app", port=PORT)