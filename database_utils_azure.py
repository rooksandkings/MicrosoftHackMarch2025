"""
Database utilities for the McKinsey scraper with Azure integration.

This module provides functions for database initialization and querying
with credentials securely stored in Azure Key Vault.
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
from dotenv import load_dotenv
from key_vault_utils import get_secret

logger = logging.getLogger(__name__)

# Load database connection from Azure Key Vault
try:
    connection_string = get_secret("DB-CONNECTION-STRING")
    logger.info("Successfully loaded database connection string from Azure Key Vault")
except Exception as e:
    logger.warning(f"Could not load connection string from Key Vault: {str(e)}")
    logger.warning("Falling back to local connection string")
    connection_string = 'sqlite:///mckinsey_data.db'

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
    
    # Relationship to article
    article = relationship("Article", back_populates="content")
    
    def __repr__(self):
        return f"<ArticleContent(id={self.id}, article_id={self.article_id})>"

def create_database():
    """Creates the database and tables if they don't exist."""
    logger.info("Creating database...")
    
    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)
    
    logger.info("Database created successfully.")
    return engine

@contextmanager
def get_session():
    """Creates and returns a session to interact with the database."""
    try:
        engine = create_engine(connection_string)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
    finally:
        session.close()

def get_database_stats():
    """Get statistics about the database tables."""
    with get_session() as session:
        article_count = session.query(Article).count()
        content_count = session.query(ArticleContent).count()
        
        return {
            "articles": article_count,
            "article_contents": content_count
        } 