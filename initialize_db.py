import os
import logging
from database_utils import Base, DB_FILE, create_engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_database():
    """Create a fresh database with all required tables."""
    try:
        # Remove existing database if it exists
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            logger.info(f"Removed existing database file: {DB_FILE}")
        
        # Create new database with all tables
        engine = create_engine(f'sqlite:///{DB_FILE}')
        Base.metadata.create_all(engine)
        logger.info(f"Successfully created new database with all tables in {DB_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    logger.info("Initializing McKinsey Scraper database...")
    success = initialize_database()
    if success:
        logger.info("Database initialization complete. You can now run the scraper.")
    else:
        logger.error("Database initialization failed. Please check the error logs.") 