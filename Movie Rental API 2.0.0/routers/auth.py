"""Router for users registration and login"""

from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import APIRouter,Depends,HTTPException,Request,Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import jose
from models import schemas
from db import db_commands,db_connection
from utils import auth_utils

templates = Jinja2Templates(directory = "/home/eduard/Desktop/Movie Rental API 2.0.0/frontend")

load_dotenv()

pwd = CryptContext(schemes= ["bcrypt"], deprecated="auto")

auth_router = APIRouter(prefix = "/auth",tags = ["Users"])

def create_user(username = Form(...),password = Form(...),email = Form(...)):
    """Create user function"""
    if len(username) >= 5 and len(username) <= 15:
        return {"username":username,"password":password,"email":email}
    raise HTTPException(detail = "Invalid username",status_code = 400)

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
        return RedirectResponse("/auth/login",status_code = 301) 

@auth_router.post("/login")
async def login_user(user = Depends(create_login_user),
                     db = Depends(db_connection.get_db)):
    async with db as connection:
        user_datas = await connection.fetchrow(db_commands.SELECT_USER_BY_USERNAME,
                                               user.get("username"))
        if user_datas is None:
            raise HTTPException(status_code = 401,detail = {"message":"invalid credentials"})
   
        hashed_password = dict(user_datas).get("password")
        if not pwd.verify(user.get("password"),hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
    
    jwt_token = await auth_utils.create_jwt_token({"username":user.get("username")})
    redirect_response = RedirectResponse(url = "/auth/home",status_code = 302)
    redirect_response.set_cookie(key = "username",value = jwt_token)
    return redirect_response
    
@auth_router.get("/home")
async def home_page(request:Request,
                    db = Depends(db_connection.get_db)):
    async with db as connection:
        movies = await connection.fetchrow(db_commands.SELECT_ALL_FROM_MOVIES)
        rentals = await connection.fetchrow(db_commands.SELECT_ALL_FROM_RENTALS)
        try:
            token = request.cookies.get("username")
            if token:
                username = await auth_utils.verify_token(token)
                if username:  
                    return templates.TemplateResponse("home_page.html", 
                                              {"request": request, "movies": movies,"rentals":
                                                  rentals,"username":username.get("username")})
                raise HTTPException(detail = {"message":"Your jwt is expired"},
                    status_code = 401)
            raise HTTPException(detail = {"message":"You are not authenticated"},status_code = 401)
        except jose.exceptions.ExpiredSignatureError:
            raise HTTPException(detail = {"message":"Your jwt is expired"},status_code = 401)

            
@auth_router.get("/logout")
async def logout():
    response = RedirectResponse("/auth/login")
    response.delete_cookie("username")
    return response
    
