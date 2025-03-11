"""
Database utilities for the McKinsey scraper.

This module provides functions for database initialization and querying.
"""

import sqlite3
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, inspect, func
from sqlalchemy.orm import sessionmaker
from mckinsey_scraper import Article, Base

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Database file
DB_FILE = 'mckinsey_articles.db'


def initialize_database():
    """
    Initialize the database and create tables if they don't exist.
    
    Returns:
        engine: SQLAlchemy engine
    """
    engine = create_engine(f'sqlite:///{DB_FILE}')
    
    # Create tables if they don't exist
    if not inspect(engine).has_table('articles'):
        logger.info("Creating database tables")
        Base.metadata.create_all(engine)
    else:
        logger.info("Database tables already exist")
    
    return engine


@contextmanager
def get_session():
    """
    Context manager for database sessions.
    
    Yields:
        Session: SQLAlchemy session
    """
    engine = initialize_database()
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()


def get_article_count():
    """
    Get the total number of articles in the database.
    
    Returns:
        int: Number of articles
    """
    with get_session() as session:
        count = session.query(func.count(Article.id)).scalar()
        return count


def get_articles(limit=10, offset=0):
    """
    Get articles from the database.
    
    Args:
        limit (int): Maximum number of articles to return
        offset (int): Offset for pagination
        
    Returns:
        list: List of Article objects
    """
    with get_session() as session:
        articles = session.query(Article).order_by(Article.scraped_at.desc()).limit(limit).offset(offset).all()
        return articles


def export_to_csv(filename='mckinsey_articles.csv'):
    """
    Export all articles to a CSV file.
    
    Args:
        filename (str): Output CSV filename
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Get all articles
        cursor.execute("SELECT title, url, description, date_published, article_type, scraped_at FROM articles")
        articles = cursor.fetchall()
        
        # Write to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            import csv
            writer = csv.writer(f)
            writer.writerow(['Title', 'URL', 'Description', 'Date Published', 'Article Type', 'Scraped At'])
            writer.writerows(articles)
        
        logger.info(f"Exported {len(articles)} articles to {filename}")
        return True
    
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return False
    
    finally:
        conn.close()


if __name__ == "__main__":
    # Example usage
    count = get_article_count()
    logger.info(f"Total articles in database: {count}")
    
    if count > 0:
        articles = get_articles(limit=5)
        logger.info("Latest 5 articles:")
        for article in articles:
            logger.info(f"- {article.title} ({article.date_published})")
        
        # Export to CSV
        export_to_csv() 