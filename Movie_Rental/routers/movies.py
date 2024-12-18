from fastapi import APIRouter,HTTPException
from models import schemas
import aiofiles
import json

movies_file = "movies.json"

movies = {}

movies_router = APIRouter(prefix = "/movies")

async def write_movies_file(data):
    with aiofiles.open(movies_file) as fs:
        await json.dumps(data,movies_file,indent=2)

async def read_movies_file(data):
    with aiofiles.open(movies_file) as fs:
        return await json.load(fs)


@movies_router.get("/")
async def list_of_movies():
    return await read_movies_file()

@movies_router.post("/")
async def add_movie(movie:schemas.Movie):
    movies = await read_movies_file()
    for movie_data in movies:
        if movie_data == movie:
            raise HTTPException(status_code = 400,detail = {"message":"movie already exists"})
    movies.update(movie)
    await write_movies_file(movies)