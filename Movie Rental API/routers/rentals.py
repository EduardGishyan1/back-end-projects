"""Rentals docstring"""

from fastapi import APIRouter,Depends
from models import schemas
from utils import auth_utils
from db import db_connection,db_commands

rental_router = APIRouter(prefix = "/rentals",tags = ["Rentals"])

@rental_router.get("/")
async def retrieve_rental_history(current_user:str = Depends(auth_utils.get_current_user),db = Depends(db_connection.get_db)):
    """Show rental history"""
    return await db.fetch(db_commands.SELECT_ALL_FROM_RENTALS,current_user)
    
@rental_router.post("/")
async def rent_movie(rental:schemas.Rental,current_user:str = Depends(auth_utils.get_current_user),db = Depends(db_connection.get_db)):
    """Rent movie"""
    await db.execute(db_commands.INSERT_INTO_RENTALS,rental.title,rental.genre,rental.rating)
    return {"message":f"success {current_user}"}
