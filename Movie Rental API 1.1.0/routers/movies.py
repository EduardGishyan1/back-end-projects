"""Movies docsrting"""

from fastapi.templating import Jinja2Templates
from fastapi import APIRouter,Depends,Request,Form
from models import schemas
from db import db_connection,db_commands

templates = Jinja2Templates(directory = "/home/eduard/Desktop/Movie Rental API/frontend")

movie_router = APIRouter(prefix = "/movies",tags = ["Movies"])

def create_movie(title = Form(...),genre = Form(...),rating = Form(...)):
    return {"title":title,"genre":genre,"rating":float(rating)}


@movie_router.get("/")
async def list_of_movies(request: Request):   
    return templates.TemplateResponse("movies.html", {"request": request})

@movie_router.post("/")
async def add_new_movie(request:Request,movie:schemas.Movie = Depends(create_movie),
                        db = Depends(db_connection.get_db)):
    """
    Adds a movie. Requires authentication.

    Args:
        movie (schemas.Movie): Movie details.
        username (str): Authenticated username.
        db: Database connection.

    Returns:
        dict: Success message.
    """
    
    async with db as connection:
        await connection.fetch(db_commands.INSERT_INTO_MOVIES,movie.get("user_id"),
                               movie.get("movie_id"),movie.get("rental_duration"))
        return templates.TemplateResponse(request,"movies.html")
