"""
McKinsey Article Scraper

This module handles scraping the full content of individual McKinsey articles
using Selenium WebDriver to render JavaScript content.
"""

import os
import time
import random
import logging
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# Import from main scraper
from mckinsey_scraper import get_user_agent, create_webdriver, Article, Base
from database_utils import get_session, store_article_content, get_unscrapped_articles, ArticleContent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Define the ArticleContent model
class ArticleContent(Base):
    """SQLAlchemy model for McKinsey article content."""
    __tablename__ = 'article_contents'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(500), unique=True, nullable=False)
    full_content = Column(Text, nullable=True)
    html_content = Column(Text, nullable=True)
    article_metadata = Column(Text, nullable=True)  # JSON string with additional metadata
    scraped_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<ArticleContent(article_id={self.article_id}, title='{self.title}')>"


def create_article_content_database():
    """Create database and tables for article content."""
    engine = create_engine('sqlite:///mckinsey_articles_content.db')
    
    # Check if the article_contents table exists
    inspector = inspect(engine)
    if not inspector.has_table('article_contents'):
        logger.info("Creating article_contents table in the content database")
        Base.metadata.create_all(engine)
    else:
        logger.info("Article contents table already exists in the content database")
    
    return engine


def get_unscrapped_articles():
    """
    Get articles that haven't had their content scraped yet.
    
    Returns:
        list: List of Article objects
    """
    engine = create_engine('sqlite:///mckinsey_articles.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # First make sure the content database exists
        content_engine = create_article_content_database()
        
        # Now try to get the URLs that have already been scraped
        scraped_urls = []
        try:
            content_session = sessionmaker(bind=content_engine)()
            scraped_urls = [url[0] for url in content_session.query(ArticleContent.url).all()]
            content_session.close()
        except Exception as e:
            # If there's an error (like table doesn't exist), log it but continue
            # with empty scraped_urls list (meaning all articles need scraping)
            logger.debug(f"Could not get scraped URLs (possibly new database): {e}")
        
        # If we have no scraped URLs, get all articles
        if not scraped_urls:
            articles = session.query(Article).all()
        else:
            # Otherwise, get articles not in scraped_urls
            articles = session.query(Article).filter(~Article.url.in_(scraped_urls)).all()
        
        return articles
    
    except Exception as e:
        logger.error(f"Error getting unscrapped articles: {e}")
        return []
    
    finally:
        session.close()


def extract_article_metadata(driver):
    """
    Extract metadata from article page.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        dict: Article metadata
    """
    metadata = {}
    
    try:
        # Try to extract author information
        author_elements = driver.find_elements(By.CSS_SELECTOR, ".author-name, .byline, [data-test='author']")
        if author_elements:
            metadata['authors'] = [elem.text.strip() for elem in author_elements]
        
        # Try to extract tags/topics
        tag_elements = driver.find_elements(By.CSS_SELECTOR, ".tag, .topic, .category, [data-test='tag']")
        if tag_elements:
            metadata['tags'] = [elem.text.strip() for elem in tag_elements]
        
        # Try to extract publication date
        date_elements = driver.find_elements(By.CSS_SELECTOR, ".date, .published-date, .article-date, [data-test='date']")
        if date_elements:
            metadata['published_date'] = date_elements[0].text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting article metadata: {e}")
    
    return metadata


def scrape_article_content(article, driver):
    """
    Scrape content for a single article.
    
    Args:
        article (Article): Article object
        driver (WebDriver): Selenium WebDriver instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Scraping article content from {article.url}")
        
        # Load the article page
        driver.get(article.url)
        
        # Wait for article content to load
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    "article, .article, .article-body, .content, main"
                ))
            )
        except TimeoutException:
            logger.warning(f"Timeout waiting for article content on {article.url}")
            # Continue anyway as we might still be able to parse some content
        
        # Get the page source
        html_content = driver.page_source
        
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Extract article metadata
        metadata = {}
        
        # Enhanced author extraction - more comprehensive patterns
        authors = []
        
        # 1. Look for standard author elements first
        author_elements = soup.select('.author-name, .author, [itemprop="author"], .byline, .contributor, .meta-author, .pb-f-article-author, [rel="author"]')
        if author_elements:
            for author_el in author_elements:
                author_text = author_el.text.strip()
                author_text = author_text.replace('By ', '').replace('by ', '').strip()
                if author_text and len(author_text) < 100:
                    authors.append(author_text)
        
        # 2. McKinsey specific pattern: Look for date_by_authors pattern
        if not authors:
            date_author_pattern = soup.find(text=lambda text: text and ('_by ' in text or ' by ' in text))
            if date_author_pattern:
                author_part = date_author_pattern.split('by ')[1].strip()
                # Clean up formatting
                author_part = author_part.replace('_', '').strip()
                # Split multiple authors
                if ',' in author_part:
                    author_list = author_part.split(',')
                    # Handle "and" in the last author
                    if ' and ' in author_list[-1]:
                        last_authors = author_list.pop().split(' and ')
                        author_list.extend(last_authors)
                    authors = [a.strip() for a in author_list if a.strip()]
                else:
                    authors = [author_part]
        
        # 3. Look for authors in the footer/bio section at the bottom
        if not authors:
            # Common patterns in McKinsey articles for author bios
            bio_indicators = ["is a partner", "is a senior partner", "is an associate partner", "is a consultant"]
            for paragraph in soup.find_all('p'):
                text = paragraph.get_text()
                if any(indicator in text.lower() for indicator in bio_indicators):
                    # This might be an author bio paragraph
                    potential_authors = []
                    # Split by commas and look for name patterns
                    segments = text.split(',')
                    for segment in segments:
                        if any(indicator in segment.lower() for indicator in bio_indicators):
                            name = segment.split(' is ')[0].strip()
                            if name and len(name) < 50:  # reasonable name length
                                potential_authors.append(name)
                    if potential_authors:
                        authors = potential_authors
                        break
        
        # Add authors to metadata
        if authors:
            metadata['authors'] = authors
            logger.info(f"Found authors: {', '.join(authors)}")
        
        # Look for published date
        date_elements = soup.select('[itemprop="datePublished"], .date, .published-date, time, .meta-date, .article-date')
        if date_elements:
            published_date = date_elements[0].text.strip()
            metadata['published_date'] = published_date
        
        # Look for tags/topics
        tag_elements = soup.select('.tag, .topic, .category, [itemprop="keywords"], .meta-tag, .article-tag')
        if tag_elements:
            tags = [tag.text.strip() for tag in tag_elements]
            metadata['tags'] = tags
        
        # Extract the main content
        # Try different selectors that might contain the main article content
        content_selectors = [
            'article', '.article', '.article-body', '.content', 'main',
            '#main-content', '.post-content', '.entry-content', '.story',
            '.article__content', '.article__body'
        ]
        
        content_element = None
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                # Take the largest element by text length
                content_element = max(elements, key=lambda e: len(e.get_text()))
                break
        
        # Extract text content
        if content_element:
            # Remove navigation, sidebars, comments, etc.
            for element in content_element.select('nav, .sidebar, .navigation, .comments, .related, .recommendations, script, style, footer'):
                element.extract()
            
            # Get the full text content
            full_content = content_element.get_text(' ', strip=True)
        else:
            # Fallback: Get the text from the body
            full_content = soup.body.get_text(' ', strip=True) if soup.body else ""
            logger.warning(f"Could not find main content element for {article.url}, using fallback")
        
        # Store the article content in the database
        success = store_article_content(
            article_id=article.id,
            title=article.title,
            url=article.url,
            html_content=html_content,
            full_content=full_content,
            article_metadata=metadata
        )
        
        return success
    
    except Exception as e:
        logger.error(f"Error scraping article content: {e}")
        return False


def scrape_all_unscrapped_articles(limit=None):
    """
    Scrape content for all articles that haven't been scrapped yet.
    """
    try:
        # Get article URLs that haven't been scrapped yet
        articles = get_unscrapped_articles()
        
        # Filter out invalid URLs
        valid_articles = []
        for article in articles:
            if "{{" in article.url or "}}" in article.url:
                logger.warning(f"Skipping article with invalid URL: {article.url}")
                continue
            valid_articles.append(article)
        
        # Apply limit after filtering
        if limit:
            valid_articles = valid_articles[:limit]
            
        if not valid_articles:
            logger.info("No unscrapped articles found")
            return 0
            
        logger.info(f"Found {len(valid_articles)} unscrapped articles. Starting content scraping...")
        
        success_count = 0
        for i, article in enumerate(valid_articles, 1):
            logger.info(f"Scraping article {i}/{len(valid_articles)}: {article.title}")
            
            # Create a WebDriver
            driver = create_webdriver()
            if not driver:
                logger.error("Failed to create WebDriver. Skipping article.")
                continue
            
            try:
                # Scrape the article content
                success = scrape_article_content(article, driver)
                if success:
                    success_count += 1
                
                # Add a random delay between requests to avoid overloading the server
                if i < len(valid_articles):
                    delay = random.uniform(3, 7)
                    logger.info(f"Waiting {delay:.2f} seconds before next request...")
                    time.sleep(delay)
                    
            finally:
                # Always close the driver
                try:
                    driver.quit()
                except:
                    pass
        
        logger.info(f"Content scraping completed. Successfully scraped {success_count}/{len(valid_articles)} articles.")
        return success_count
    
    except Exception as e:
        logger.error(f"Error in scrape_all_unscrapped_articles: {e}")
        return 0


if __name__ == "__main__":
    logger.info("Starting McKinsey article content scraper with Selenium WebDriver")
    
    # Scrape up to 5 unscrapped articles in test mode
    article_count = scrape_all_unscrapped_articles(limit=5)
    
    logger.info(f"Article content scraping completed. Scraped {article_count} articles.") 