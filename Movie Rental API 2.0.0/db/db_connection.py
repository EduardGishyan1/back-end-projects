"""connection of db"""

import os
from contextlib import asynccontextmanager
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


@asynccontextmanager
async def get_db():
    """Get Database"""
    
    pool = await asyncpg.create_pool(DATABASE_URL)
    async with pool.acquire() as connect:
        yield connect
    await pool.close()
   