"""Main file"""

import os
from contextlib import asynccontextmanager
import uvicorn
import asyncpg
from fastapi import FastAPI,Request

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
    try:
        async with app.state.pool.acquire() as connect:
            await connect.fetchrow(db_commands.CREATE_TABLE_USERS),
            await connect.fetchrow(db_commands.CREATE_TABLE_MOVIES),
            await connect.fetchrow(db_commands.CREATE_TABLE_RENTALS)
        yield
    finally:
        await app.state.pool.close()

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def allow_all_requests(request:Request,call_next):
    """Allow all of clients request"""
    response = await call_next(request)
    return response

app.include_router(auth.auth_router)
app.include_router(movies.movie_router)
app.include_router(rentals.rental_router)

if __name__ == "__main__":
    uvicorn.run("main:app",host=HOST,port=PORT,reload=True)
