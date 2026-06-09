import logging
import asyncio
from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.db.init_db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init():
    logger.info("Creating database tables if they don't exist")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    logger.info("Initializing database with seed data")
    async with SessionLocal() as db:
        await init_db(db)
    logger.info("Initialization complete")

def main() -> None:
    asyncio.run(init())

if __name__ == "__main__":
    main()
