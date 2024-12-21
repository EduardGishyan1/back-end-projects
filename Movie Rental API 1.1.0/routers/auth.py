"""Router for users registration and login"""

from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import APIRouter,Depends,HTTPException,Request,Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from models import schemas
from db import db_commands,db_connection

templates = Jinja2Templates(directory = "/home/eduard/Desktop/Movie Rental API/frontend")

load_dotenv()

pwd = CryptContext(schemes= ["bcrypt"], deprecated="auto")

auth_router = APIRouter(prefix = "/auth",tags = ["Users"])

def create_user(username = Form(...),password = Form(...),email = Form(...)):
    return {"username":username,"password":password,"email":email}

def create_login_user(username = Form(...),password = Form(...)):
    return {"username":username,"password":password}


@auth_router.get("/register")
async def register_page(request:Request):
    return templates.TemplateResponse(request,"register.html")

@auth_router.get("/login")
async def login_page(request:Request):
    return templates.TemplateResponse(request,"login.html")

@auth_router.post("/register")
async def register_user(user:schemas.User = Depends(create_user),
                        db = Depends(db_connection.get_db)):
    """User Registration"""
    async with db as connection:
        existing_user = await connection.fetchrow(db_commands.SELECT_USER_BY_USERNAME,
                                                  user.get("username"))
        if existing_user:
            raise HTTPException(status_code = 400,
                                detail = {"message":"User already exists"})
        existing_email = await connection.fetchrow(db_commands.SELECT_USER_BY_EMAIL,
                                                   user.get("email"))
        if existing_email:
            raise HTTPException(status_code = 400,detail = {"message":"Email already exists"})

        hashed_password = pwd.hash(user.get("password"))
        await connection.fetchrow(db_commands.INSERT_INTO_USERS,user.get("username"),
                                  hashed_password,user.get("email"))
        return RedirectResponse("/auth/home",status_code = 301) 

@auth_router.post("/login")
async def create_login_user(user = Depends(create_login_user),
                     db = Depends(db_connection.get_db)):
    async with db as connection:
        user_datas = await connection.fetchrow(db_commands.SELECT_USER_BY_USERNAME,
                                               user.get("username"))
        if user_datas is None:
            raise HTTPException(status_code = 401,detail = {"message":"invalid credentials"})
   
        hashed_password = dict(user_datas).get("password")
        if not pwd.verify(user.get("password"),hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    return RedirectResponse(url = "/auth/home",status_code = 302)
    
@auth_router.get("/home")
async def home_page(request:Request,
                    db = Depends(db_connection.get_db)):
    try:
        async with db as connection:
            movies = await connection.fetchrow(db_commands.SELECT_ALL_FROM_MOVIES)
            rentals = await connection.fetchrow(db_commands.SELECT_ALL_FROM_RENTALS)
            return templates.TemplateResponse("home_page.html", 
                                              {"request": request, "movies": movies,
                                               "rentals":rentals})
    except Exception as e:
        print(f"Error fetching movies: {e}")
       
            
@auth_router.get("/logout")
async def logout():
    response = RedirectResponse("/auth/login")
    response.delete_cookie("username")
    return response
    