"""connection of db"""

import os
import asyncpg
from dotenv import load_dotenv
from db import db_commands

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_connection_pool():
    """Connection pool"""
    return await asyncpg.create_pool(DATABASE_URL)

async def get_db():
    """Get Database"""
    pool = await get_connection_pool()
    async with pool.acquire() as connect:
        await connect.fetchrow(db_commands.CREATE_TABLE_MOVIES)
        await connect.fetchrow(db_commands.CREATE_TABLE_RENTALS)
        await connect.fetchrow(db_commands.CREATE_TABLE_USERS)
        yield connect
