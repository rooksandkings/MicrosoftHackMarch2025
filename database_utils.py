"""
Database utilities for the McKinsey scraper.

This module provides functions for database initialization and querying.
"""

import json
import sqlite3
import logging
import csv
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Define a single database file
DB_FILE = 'mckinsey_data.db'
Base = declarative_base()

# Define models
class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    url = Column(String(500), unique=True)
    description = Column(Text, nullable=True)
    date_published = Column(String(100), nullable=True)
    article_type = Column(String(100), nullable=True)
    scraped_at = Column(DateTime, default=datetime.now)
    
    # Relationship to content
    content = relationship("ArticleContent", back_populates="article", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title}')>"

class ArticleContent(Base):
    __tablename__ = 'article_contents'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'))
    title = Column(String(500))
    url = Column(String(500))
    html_content = Column(Text, nullable=True)
    full_content = Column(Text, nullable=True)
    authors = Column(Text, nullable=True)
    article_metadata = Column(Text, nullable=True)  # JSON-serialized metadata
    processed = Column(Boolean, default=False)
    scraped_at = Column(DateTime, default=datetime.now)
    
    # Relationship to article
    article = relationship("Article", back_populates="content")
    
    def __repr__(self):
        return f"<ArticleContent(id={self.id}, article_id={self.article_id})>"

def create_database():
    """
    Create the database and tables if they don't exist.
    
    Returns:
        sqlalchemy.engine.Engine: Database engine
    """
    try:
        engine = create_engine(f'sqlite:///{DB_FILE}')
        # Create all tables defined by the Base metadata
        Base.metadata.create_all(engine)
        logger.info(f"Database initialized in {DB_FILE}")
        return engine
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return None

@contextmanager
def get_session():
    """
    Get a database session.
    
    Yields:
        Session: Database session
    """
    engine = create_database()
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def store_article(article_data):
    """
    Store article data in the database.
    
    Args:
        article_data (dict): Article data to store
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with get_session() as session:
            # Check if article already exists
            existing = session.query(Article).filter_by(url=article_data['url']).first()
            if existing:
                logger.info(f"Article already exists: {article_data['title']}")
                return False
                
            # Create new article
            article = Article(
                title=article_data['title'],
                url=article_data['url'],
                description=article_data.get('description', ''),
                date_published=article_data.get('date_published', ''),
                article_type=article_data.get('article_type', 'Article'),
                scraped_at=datetime.now()
            )
            session.add(article)
            session.commit()
            logger.info(f"Stored article: {article_data['title']}")
            return True
            
    except Exception as e:
        logger.error(f"Error storing article: {e}")
        return False

def get_unscrapped_articles(limit=None):
    """
    Get all articles that haven't been scrapped for content yet.
    
    Args:
        limit (int, optional): Maximum number of articles to return
        
    Returns:
        list: List of Article objects
    """
    try:
        with get_session() as session:
            # Get articles that don't have corresponding content
            subquery = session.query(ArticleContent.article_id)
            query = session.query(Article).filter(~Article.id.in_(subquery))
            
            if limit:
                query = query.limit(limit)
                
            articles = query.all()
            return articles
    except Exception as e:
        logger.error(f"Error getting unscrapped articles: {e}")
        return []

def store_article_content(article_id, title, url, html_content, full_content, article_metadata):
    """
    Store article content in the database.
    
    Args:
        article_id (int): Article ID
        title (str): Article title
        url (str): Article URL
        html_content (str): HTML content
        full_content (str): Full text content
        article_metadata (dict): Article metadata
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Extract authors from metadata if available
        authors = None
        if article_metadata and 'authors' in article_metadata:
            authors = ', '.join(article_metadata['authors'])
            
        with get_session() as session:
            # Check if article content already exists
            existing = session.query(ArticleContent).filter_by(article_id=article_id).first()
            if existing:
                logger.info(f"Article content for article ID {article_id} already exists")
                return False
                
            # Create new article content
            article_content = ArticleContent(
                article_id=article_id,
                title=title,
                url=url,
                html_content=html_content,
                full_content=full_content,
                authors=authors,  # Store authors as string
                article_metadata=json.dumps(article_metadata) if article_metadata else None
            )
            
            session.add(article_content)
            logger.info(f"Stored content for article: {title}")
            return True
    
    except Exception as e:
        logger.error(f"Error storing article content: {e}")
        return False

def get_articles(limit=10, offset=0):
    """
    Get a list of articles from the database.
    
    Args:
        limit (int): Maximum number of articles to return
        offset (int): Offset for pagination
        
    Returns:
        list: List of Article objects
    """
    try:
        with get_session() as session:
            articles = session.query(Article).order_by(Article.scraped_at.desc()).offset(offset).limit(limit).all()
            return articles
    except Exception as e:
        logger.error(f"Error getting articles: {e}")
        return []

def get_article_contents(limit=10, offset=0):
    """
    Get a list of article contents from the database.
    
    Args:
        limit (int): Maximum number of article contents to return
        offset (int): Offset for pagination
        
    Returns:
        list: List of ArticleContent objects
    """
    try:
        with get_session() as session:
            contents = session.query(ArticleContent).order_by(ArticleContent.scraped_at.desc()).offset(offset).limit(limit).all()
            return contents
    except Exception as e:
        logger.error(f"Error getting article contents: {e}")
        return []

def export_to_csv(filename='mckinsey_articles.csv'):
    """
    Export all articles to a CSV file.
    
    Args:
        filename (str): Output CSV filename
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with get_session() as session:
            articles = session.query(Article).all()
            
            if not articles:
                logger.warning("No articles found to export")
                return False
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Title', 'URL', 'Description', 'Date Published', 'Article Type', 'Scraped At'])
                
                for article in articles:
                    writer.writerow([
                        article.id,
                        article.title,
                        article.url,
                        article.description,
                        article.date_published,
                        article.article_type,
                        article.scraped_at
                    ])
            
            logger.info(f"Exported {len(articles)} articles to {filename}")
            return True
    
    except Exception as e:
        logger.error(f"Error exporting articles to CSV: {e}")
        return False

def export_content_to_csv(filename='articles_content.csv'):
    """
    Export all article contents to a CSV file.
    
    Args:
        filename (str): Output CSV filename
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with get_session() as session:
            contents = session.query(ArticleContent).all()
            
            if not contents:
                logger.warning("No article contents found to export. Run 'scrape-content' command first.")
                return False
            
            # Filter out entries with template placeholders or 'Access Denied'
            valid_contents = []
            for content in contents:
                if "{{" in content.url or "}}" in content.url:
                    logger.warning(f"Skipping invalid article: {content.title} with URL {content.url}")
                    continue
                if content.full_content and "Access Denied" in content.full_content[:20]:
                    logger.warning(f"Skipping article with access denied: {content.title}")
                    continue
                valid_contents.append(content)
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Article ID', 'Title', 'URL', 'Authors', 'Full Content', 'Article Metadata', 'Scraped At'])
                
                for content in valid_contents:
                    writer.writerow([
                        content.article_id,
                        content.title,
                        content.url,
                        content.authors or '',  # Include authors in CSV
                        content.full_content,
                        content.article_metadata,
                        content.scraped_at
                    ])
            
            logger.info(f"Exported {len(valid_contents)} valid article contents to {filename}")
            return True
    
    except Exception as e:
        logger.error(f"Error exporting article contents to CSV: {e}")
        return False

def get_database_stats():
    """
    Get statistics about the database.
    
    Returns:
        dict: Database statistics
    """
    try:
        with get_session() as session:
            total_articles = session.query(Article).count()
            total_contents = session.query(ArticleContent).count()
            
            return {
                'total_articles': total_articles,
                'articles_with_content': total_contents,
                'articles_without_content': total_articles - total_contents
            }
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {
            'total_articles': 0,
            'articles_with_content': 0,
            'articles_without_content': 0
        }

def get_article_count():
    """
    Get the total count of articles in the database.
    
    Returns:
        int: Total number of articles
    """
    try:
        with get_session() as session:
            count = session.query(Article).count()
            return count
    except Exception as e:
        logger.error(f"Error getting article count: {e}")
        return 0

def get_article_content_count():
    """
    Get the total count of article contents in the database.
    
    Returns:
        int: Total number of article contents
    """
    try:
        with get_session() as session:
            count = session.query(ArticleContent).count()
            return count
    except Exception as e:
        logger.error(f"Error getting article content count: {e}")
        return 0

def check_database_tables():
    """
    Check if the required database tables exist.
    
    Returns:
        tuple: (articles_exists, contents_exists)
    """
    try:
        engine = create_engine(f'sqlite:///{DB_FILE}')
        inspector = inspect(engine)
        
        articles_exists = 'articles' in inspector.get_table_names()
        contents_exists = 'article_contents' in inspector.get_table_names()
        
        return articles_exists, contents_exists
    except Exception as e:
        logger.error(f"Error checking database tables: {e}")
        return False, False

if __name__ == "__main__":
    # Example usage
    stats = get_database_stats()
    logger.info(f"Total articles: {stats['total_articles']}")
    logger.info(f"Articles with content: {stats['articles_with_content']}")
    logger.info(f"Articles without content: {stats['articles_without_content']}")
    
    if stats['total_articles'] > 0:
        articles = get_articles(limit=5)
        logger.info("Latest 5 articles:")
        for article in articles:
            logger.info(f"- {article.title} ({article.date_published})")
        
        # Export to CSV
        export_to_csv()
    
    if stats['articles_with_content'] > 0:
        contents = get_article_contents(limit=5)
        logger.info("Latest 5 article contents:")
        for content in contents:
            logger.info(f"- {content.title}")
        
        # Export to CSV
        export_content_to_csv() 