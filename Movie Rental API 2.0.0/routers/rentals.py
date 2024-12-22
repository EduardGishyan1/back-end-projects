"""Rentals docstring"""

from fastapi.templating import Jinja2Templates
from fastapi import APIRouter,Depends,Form,Request,HTTPException
from fastapi.responses import RedirectResponse
from models import schemas
from db import db_connection,db_commands
from utils import auth_utils

rental_router = APIRouter(prefix = "/rentals",tags = ["Rentals"])

templates = Jinja2Templates(directory = "/home/eduard/Desktop/Movie Rental API 1.1.0/frontend")

def create_rental(user_id = Form(...),movie_id = Form(...),
                  rental_duration = Form(...)):
    return {"user_id":int(user_id),"movie_id":int(movie_id),
            "rental_duration":float(rental_duration)}
    
@rental_router.get("/")
async def get_rentals(request:Request):
    token = request.cookies.get("username")
    if token:
        username = await auth_utils.verify_token(token)
        if username:
            return templates.TemplateResponse("rentals.html", {"request": request})
        return HTTPException(detail = {"message":"Your jwt is expired"},status_code = 401)
    return HTTPException(detail = {"message":"You are not authenticated"},status_code = 401)


@rental_router.post("/")
async def rent_movie(rental:schemas.Rental = Depends(create_rental),
                     db = Depends(db_connection.get_db)):
    """Rent movie"""
    async with db as connection:
        await connection.fetch(db_commands.INSERT_INTO_RENTALS,rental.get("user_id"),
                               rental.get("movie_id"),rental.get("rental_duration"))
        return RedirectResponse("/auth/home",status_code = 303)