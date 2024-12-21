"""Main file"""

import os
import uvicorn
import asyncpg
from fastapi import FastAPI
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from routers import auth,movies,rentals
from db import db_connection,db_commands

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PORT = int(os.getenv("PORT"))
HOST = os.getenv("HOST")

@asynccontextmanager
async def lifespan(app:FastAPI):
    '''Applications Start point'''
    db_connection.get_db()
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)
    async with app.state.pool.acquire() as connect:
        await connect.fetch(db_commands.CREATE_TABLE_USERS),
        await connect.fetchrow(db_commands.CREATE_TABLE_MOVIES),
        await connect.fetchrow(db_commands.CREATE_TABLE_RENTALS)
    yield
    await app.state.pool.close()

app = FastAPI(lifespan=lifespan)

app.include_router(auth.auth_router)
app.include_router(movies.movie_router)
app.include_router(rentals.rental_router)

if __name__ == "__main__":
    uvicorn.run("main:app",host=HOST,port=PORT,reload=True)
