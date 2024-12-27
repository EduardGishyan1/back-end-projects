"""Movies docsrting"""

from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import APIRouter,Depends,Request,Form,HTTPException
import jose
from models import schemas
from db import db_connection,db_commands
from utils import auth_utils

templates = Jinja2Templates(directory = "/home/eduard/Desktop/Movie Rental API 2.0.0/frontend")

movie_router = APIRouter(prefix = "/movies",tags = ["Movies"])

def create_movie(title = Form(...),genre = Form(...),rating = Form(...)):
    return {"title":title,"genre":genre,"rating":float(rating)}


@movie_router.get("/")
async def list_of_movies(request: Request):
    try:
        token = request.cookies.get("username")
        if token:
            username = await auth_utils.verify_token(token)
            if username:
                return templates.TemplateResponse("movies.html", {"request": request})
            raise HTTPException(detail = {"message":"Your jwt is expired"},status_code = 401)
        raise HTTPException(detail = {"message":"You are not authenticated"},status_code = 401)
    except jose.exceptions.ExpiredSignatureError:
        raise HTTPException(detail = {"message":"Your jwt is expired"},status_code = 401)


@movie_router.post("/")
async def add_new_movie(movie:schemas.User = Depends(create_movie),
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
        await connection.fetch(db_commands.INSERT_INTO_MOVIES,movie.get("title"),
                               movie.get("genre"),movie.get("rating"))
        return RedirectResponse("/auth/home",status_code = 303)
