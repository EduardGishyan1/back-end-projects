"""connection of db"""

import os
from contextlib import asynccontextmanager
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_connection_pool():
    """Connection pool"""
    return await asyncpg.create_pool(DATABASE_URL)

@asynccontextmanager
async def get_db():
    """Get Database"""
    try:
        pool = await get_connection_pool()
        async with pool.acquire() as connect:
            yield connect
    except asyncpg.exceptions.TooManyConnectionsError:
        return