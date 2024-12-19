"""Movies docsrting"""

from fastapi import APIRouter,Depends
from models import schemas
from utils import auth_utils
from db import db_connection,db_commands

movie_router = APIRouter(prefix = "/movies",tags = ["Movies"])

@movie_router.get("/")
async def list_of_movies(db = Depends(db_connection.get_db)):
    """Get list of movies"""
    return await db.fetch(db_commands.SELECT_ALL_FROM_MOVIES)
    
@movie_router.post("/")
async def add_new_movie(movie:schemas.Movie,current_user:str = Depends(auth_utils.get_current_user), db = Depends(db_connection.get_db)):
    """
    Adds a movie. Requires authentication.

    Args:
        movie (schemas.Movie): Movie details.
        username (str): Authenticated username.
        db: Database connection.

    Returns:
        dict: Success message.
    """
    await db.fetch(db_commands.INSERT_INTO_MOVIES,movie.title,movie.genre,movie.rating)
    return {"message":f"success {current_user}"}
