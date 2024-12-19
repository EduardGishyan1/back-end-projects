"""Main file"""

import os
import uvicorn
import asyncpg
from fastapi import FastAPI
from dotenv import load_dotenv
from routers import auth,movies,rentals

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PORT = int(os.getenv("PORT"))
HOST = os.getenv("HOST")

async def lifespan(app:FastAPI):
    '''Applications Start point'''
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)
    yield
    await app.state.pool.close()

app = FastAPI(lifespan=lifespan)

app.include_router(auth.auth_router)
app.include_router(movies.movie_router)
app.include_router(rentals.rental_router)

if __name__ == "__main__":
    uvicorn.run("main:app",host=HOST,port=PORT,reload=True)
