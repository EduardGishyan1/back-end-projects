from fastapi import APIRouter
from models import schemas
import aiofiles
import json

rentals_file = "rentals.json"

rentals = {}

rentals_router = APIRouter(prefix = "/rentals")

@rentals_router.post('/')
def rent_movie(rental:schemas.Rental):
    pass

@rentals_router.get("/")
def movie_history():
    return rentals