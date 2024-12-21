"""Rentals docstring"""

from fastapi.templating import Jinja2Templates
from fastapi import APIRouter,Depends,Form,Request
from models import schemas
from db import db_connection,db_commands

rental_router = APIRouter(prefix = "/rentals",tags = ["Rentals"])

templates = Jinja2Templates(directory = "/home/eduard/Desktop/Movie Rental API/frontend")

def create_rental(user_id = Form(...),movie_id = Form(...),
                  rental_duration = Form(...)):
    return {"user_id":int(user_id),"movie_id":int(movie_id),
            "rental_duration":float(rental_duration)}

@rental_router.post("/")
async def rent_movie(request:Request,rental:schemas.Rental = Depends(create_rental),
                     db = Depends(db_connection.get_db)):
    """Rent movie"""
    async with db as connection:
        await connection.fetch(db_commands.INSERT_INTO_RENTALS,rental.get("user_id"),
                               rental.get("movie_id"),rental.get("rental_duration"))
        return templates.TemplateResponse(request,"rentals.html")