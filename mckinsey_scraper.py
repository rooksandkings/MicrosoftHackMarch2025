"""
McKinsey Search Results Scraper

This script scrapes search results from McKinsey's website and stores them in an SQL database.
"""

import os
import time
import random
import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Base URL for search
BASE_URL = "https://www.mckinsey.com/search"
SEARCH_QUERY = "change management"

# Database setup
Base = declarative_base()

class Article(Base):
    """SQLAlchemy model for McKinsey articles."""
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    url = Column(String(500), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    date_published = Column(String(100), nullable=True)
    article_type = Column(String(100), nullable=True)
    scraped_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Article(title='{self.title}', url='{self.url}')>"


def create_database():
    """Create database and tables."""
    engine = create_engine('sqlite:///mckinsey_articles.db')
    Base.metadata.create_all(engine)
    return engine


def get_user_agent():
    """Generate a random user agent."""
    ua = UserAgent()
    return ua.random


def fetch_page(url, params=None, retries=3):
    """
    Fetch a webpage with retry logic.
    
    Args:
        url (str): URL to fetch
        params (dict, optional): URL parameters
        retries (int): Number of retry attempts
        
    Returns:
        str: HTML content or None if failed
    """
    headers = {
        'User-Agent': get_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    for attempt in range(retries):
        try:
            logger.info(f"Fetching {url} with params {params}")
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            if attempt < retries - 1:
                sleep_time = random.uniform(2, 5) * (attempt + 1)
                logger.info(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            else:
                logger.error(f"Failed to fetch {url} after {retries} attempts")
                return None


def parse_articles(html_content):
    """
    Parse article information from HTML content.
    
    Args:
        html_content (str): HTML content to parse
        
    Returns:
        list: List of article dictionaries
    """
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'lxml')
    articles = []
    
    # Find search result items
    search_results = soup.select('.search-result-item')
    
    for result in search_results:
        try:
            # Extract article data
            title_elem = result.select_one('.search-result-item__title')
            link_elem = title_elem.find('a') if title_elem else None
            
            title = title_elem.text.strip() if title_elem else "No title"
            url = "https://www.mckinsey.com" + link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""
            
            description_elem = result.select_one('.search-result-item__description')
            description = description_elem.text.strip() if description_elem else ""
            
            date_elem = result.select_one('.search-result-item__date')
            date_published = date_elem.text.strip() if date_elem else ""
            
            type_elem = result.select_one('.search-result-item__type')
            article_type = type_elem.text.strip() if type_elem else ""
            
            article = {
                'title': title,
                'url': url,
                'description': description,
                'date_published': date_published,
                'article_type': article_type,
            }
            
            articles.append(article)
            logger.info(f"Parsed article: {title}")
            
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
    
    return articles


def store_articles(engine, articles):
    """
    Store articles in the database.
    
    Args:
        engine: SQLAlchemy engine
        articles (list): List of article dictionaries
        
    Returns:
        int: Number of articles stored
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    stored_count = 0
    try:
        for article_data in articles:
            # Check if article already exists
            existing = session.query(Article).filter_by(url=article_data['url']).first()
            if not existing:
                article = Article(
                    title=article_data['title'],
                    url=article_data['url'],
                    description=article_data['description'],
                    date_published=article_data['date_published'],
                    article_type=article_data['article_type'],
                )
                session.add(article)
                stored_count += 1
        
        session.commit()
        logger.info(f"Stored {stored_count} new articles in the database")
    except Exception as e:
        session.rollback()
        logger.error(f"Error storing articles: {e}")
    finally:
        session.close()
    
    return stored_count


def get_total_pages(html_content):
    """
    Extract the total number of pages from search results.
    
    Args:
        html_content (str): HTML content
        
    Returns:
        int: Total number of pages or 1 if not found
    """
    if not html_content:
        return 1
    
    soup = BeautifulSoup(html_content, 'lxml')
    pagination = soup.select_one('.search-pagination')
    
    if not pagination:
        return 1
    
    # Try to find the last page number
    page_items = pagination.select('.search-pagination__item')
    
    if not page_items:
        return 1
    
    try:
        # The second-to-last item is often the last page number
        # (last is often the "next" button)
        last_page = int(page_items[-2].text.strip())
        return last_page
    except (IndexError, ValueError):
        logger.warning("Could not determine total pages, defaulting to 1")
        return 1


def scrape_mckinsey_search(query, test_mode=True):
    """
    Main function to scrape McKinsey search results.
    
    Args:
        query (str): Search query
        test_mode (bool): If True, only scrape the first page
        
    Returns:
        int: Total number of articles scraped
    """
    # Create database and tables
    engine = create_database()
    
    params = {
        'q': query,
    }
    
    # Fetch first page
    html_content = fetch_page(BASE_URL, params)
    if not html_content:
        logger.error("Failed to fetch first page")
        return 0
    
    # Parse and store articles from first page
    articles = parse_articles(html_content)
    stored_count = store_articles(engine, articles)
    
    if test_mode:
        logger.info("Test mode: Only scraping first page")
        return stored_count
    
    # Get total number of pages
    total_pages = get_total_pages(html_content)
    logger.info(f"Found {total_pages} pages of search results")
    
    # Scrape remaining pages
    for page in range(2, total_pages + 1):
        logger.info(f"Scraping page {page} of {total_pages}")
        
        # Add page parameter
        params['page'] = page
        
        # Add delay to avoid rate limiting
        time.sleep(random.uniform(3, 7))
        
        # Fetch page
        html_content = fetch_page(BASE_URL, params)
        if not html_content:
            logger.error(f"Failed to fetch page {page}")
            continue
        
        # Parse and store articles
        articles = parse_articles(html_content)
        stored_count += store_articles(engine, articles)
    
    return stored_count


if __name__ == "__main__":
    logger.info("Starting McKinsey search scraper")
    
    # Initial deployment - test mode (first page only)
    article_count = scrape_mckinsey_search(SEARCH_QUERY, test_mode=True)
    
    logger.info(f"Scraping completed. Stored {article_count} articles.") 