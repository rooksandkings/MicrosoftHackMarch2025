#!/usr/bin/env python3
"""
Test Database Connection Script
-------------------------------
Verifies that the database connection works properly with 
Azure Key Vault integration.
"""

import logging
import sys
import os
from database_utils_azure import create_database, get_database_stats, get_session, Article

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestConnection")

def test_read():
    """Test reading from the database."""
    logger.info("Testing read operations...")
    
    stats = get_database_stats()
    logger.info(f"Database stats: {stats}")
    
    with get_session() as session:
        articles = session.query(Article).limit(5).all()
        
        if articles:
            logger.info(f"Successfully read {len(articles)} articles from database")
            for article in articles:
                logger.info(f"Article: {article.title}")
        else:
            logger.info("No articles found in database")
    
    return True

def test_write():
    """Test writing to the database."""
    logger.info("Testing write operations...")
    
    from datetime import datetime
    
    with get_session() as session:
        # Create a test article
        test_article = Article(
            title="Test Article from Azure Foundry",
            url="https://example.com/test-article",
            description="This is a test article created to verify database connectivity",
            date_published=datetime.now().strftime("%Y-%m-%d"),
            article_type="Test",
            scraped_at=datetime.now()
        )
        
        session.add(test_article)
        session.commit()
        
        logger.info(f"Successfully created test article with ID: {test_article.id}")
    
    return True

def main():
    logger.info("Testing database connection with Azure Key Vault integration...")
    
    try:
        # Create database if it doesn't exist
        create_database()
        
        # Test reading from database
        read_success = test_read()
        
        # Test writing to database
        write_success = test_write()
        
        if read_success and write_success:
            logger.info("Database connection test completed successfully!")
            return 0
        else:
            logger.error("Database connection test failed")
            return 1
            
    except Exception as e:
        logger.exception(f"Error during database connection test: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 