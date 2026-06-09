import logging
from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.db.init_db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    logger.info("Creating database tables if they don't exist")
    Base.metadata.create_all(bind=engine)
    logger.info("Initializing database with seed data")
    db = SessionLocal()
    try:
        init_db(db)
        logger.info("Initialization complete")
    finally:
        db.close()

if __name__ == "__main__":
    main()
