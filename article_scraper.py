"""
McKinsey Article Scraper

This module handles scraping the full content of individual McKinsey articles
using Selenium WebDriver to directly access and parse DOM structure.
"""

import os
import time
import random
import logging
import json
import csv
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, WebDriverException, NoSuchElementException, 
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create base for models
Base = declarative_base()

# Define ArticleContent model
class ArticleContent(Base):
    __tablename__ = 'article_contents'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer)
    url = Column(String(500), unique=True)
    title = Column(String(500), nullable=False)
    full_content = Column(Text)
    html_content = Column(Text)
    article_metadata = Column(Text)  # JSON string
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ArticleContent(id={self.id}, article_id={self.article_id}, title={self.title})>"

# Define Article model (corrected to match actual database schema)
class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    url = Column(String(500))
    content = Column(Text)  # Changed from summary to content
    author = Column(String(255))
    publication_date = Column(String(255))
    word_count = Column(Integer)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title})>"

def create_article_content_database():
    """Create database and tables for article content."""
    engine = create_engine('sqlite:///mckinsey_articles_content.db')
    
    # Create all tables
    Base.metadata.create_all(engine)
    logger.info("Article content database and tables created.")
    
    return engine

def get_session():
    """Get a database session."""
    engine = create_engine('sqlite:///mckinsey_articles_content.db')
    Session = sessionmaker(bind=engine)
    return Session()

def get_article_database_session():
    """Get a session for the main articles database."""
    engine = create_engine('sqlite:///mckinsey_data.db')
    Session = sessionmaker(bind=engine)
    return Session()

def get_unscrapped_articles(limit=None):
    """
    Get articles that haven't been scrapped for content yet.
    
    Args:
        limit: Maximum number of articles to return
        
    Returns:
        List of Article objects
    """
    try:
        # Get a session for the main articles database
        article_session = get_article_database_session()
        
        # Inspect the actual database schema
        inspector = inspect(article_session.bind)
        table_names = inspector.get_table_names()
        
        if 'articles' not in table_names:
            logger.error("Articles table not found in database")
            return []
            
        # Get the actual column names from the database
        columns = [c['name'] for c in inspector.get_columns('articles')]
        logger.info(f"Found articles table with columns: {columns}")
        
        # Build a dynamic query based on actual columns
        from sqlalchemy import table, column, select
        
        # Create a dynamic table object
        articles_table = table('articles', 
            *[column(c) for c in columns]
        )
        
        # Execute raw query to get all articles
        result = article_session.execute(select(articles_table))
        articles_data = result.fetchall()
        
        # Convert raw data to Article-like objects
        articles = []
        for row in articles_data:
            article = type('Article', (), {})  # Create a dynamic object
            for i, col in enumerate(columns):
                setattr(article, col, row[i])
            articles.append(article)
        
        # Get content database session
        content_session = get_session()
        
        # Check if article_contents table exists
        content_inspector = inspect(content_session.bind)
        if 'article_contents' not in content_inspector.get_table_names():
            logger.info("Creating article_contents table")
            Base.metadata.create_all(content_session.bind)
        
        # Get URLs of articles that already have content
        try:
            content_urls = [row[0] for row in content_session.query(ArticleContent.url).all()]
        except Exception as e:
            logger.warning(f"Could not query article_contents: {e}")
            content_urls = []
        
        # Filter out articles that already have content
        unscrapped = []
        for article in articles:
            if hasattr(article, 'url') and article.url not in content_urls:
                unscrapped.append(article)
        
        content_session.close()
        article_session.close()
        
        logger.info(f"Found {len(unscrapped)} articles that need content scraping")
        
        if limit:
            return unscrapped[:limit]
        return unscrapped
        
    except Exception as e:
        logger.error(f"Error getting unscrapped articles: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def create_webdriver(headless=True):
    """Create and configure a Chrome WebDriver."""
    try:
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
            
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Install ChromeDriver if not present
        webdriver_service = Service(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
        driver.set_page_load_timeout(30)
        
        return driver
        
    except Exception as e:
        logger.error(f"Error creating WebDriver: {e}")
        return None

def store_article_content(article, url, html_content, content_text, metadata):
    """Store article content in database."""
    try:
        session = get_session()
        
        # Check if article already exists in content database
        existing = session.query(ArticleContent).filter_by(url=url).first()
        
        if existing:
            logger.info(f"Article content already exists for URL: {url}. Updating...")
            existing.html_content = html_content
            existing.full_content = content_text
            existing.article_metadata = json.dumps(metadata)
            existing.scraped_at = datetime.utcnow()
        else:
            # Create new article content
            article_content = ArticleContent(
                article_id=article.id,
                url=url,
                title=article.title,
                html_content=html_content,
                full_content=content_text,
                article_metadata=json.dumps(metadata),
                scraped_at=datetime.utcnow()
            )
            session.add(article_content)
        
        session.commit()
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"Error storing article content: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False

def extract_content_from_dom(driver):
    """
    Extract article content directly from DOM structure without using regex.
    
    This function uses direct DOM traversal for more precise content extraction.
    """
    try:
        # Wait for article content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
        
        # Check page title to ensure we're on a valid article
        title = driver.title
        if not title or len(title) < 5:
            logger.warning("Page title is missing or too short - page may not have loaded properly")
            time.sleep(5)  # Wait longer to see if page loads
            title = driver.title
        
        # First check if we hit a paywall or login prompt
        paywall_indicators = [
            "//div[contains(@class, 'paywall')]",
            "//div[contains(@class, 'subscription')]",
            "//div[contains(text(), 'Please subscribe')]",
            "//div[contains(text(), 'Sign in')]",
            "//div[contains(@class, 'login')]"
        ]
        
        for indicator in paywall_indicators:
            elements = driver.find_elements(By.XPATH, indicator)
            if elements and len(elements) > 0:
                logger.warning("Paywall or login requirement detected")
                return {
                    "content": "PAYWALL DETECTED: Content not accessible",
                    "metadata": {"error": "paywall"}
                }
                
        # Primary content extraction - try different selectors
        content_selectors = [
            "div.article-content", 
            "div.main-content",
            "article main",
            "#article-content",
            ".article-body",
            ".article-body-container",
            "article .content",
            ".post-content",
            "main"
        ]
        
        content_element = None
        for selector in content_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements and len(elements) > 0:
                # Find the largest content element by text length
                if len(elements) > 1:
                    content_element = max(elements, key=lambda e: len(e.text))
                else:
                    content_element = elements[0]
                break
        
        if not content_element:
            logger.warning("Could not find article content container")
            # Try a more generic approach
            content_element = driver.find_element(By.TAG_NAME, "body")
        
        # Before extracting content, ensure there's enough text
        content_text_length = len(content_element.text)
        if content_text_length < 500:
            logger.warning(f"Content suspiciously short ({content_text_length} chars), waiting longer...")
            time.sleep(5)
            # Refresh content element
            if selector:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and len(elements) > 0:
                    content_element = elements[0]
        
        # Get HTML content
        html_content = content_element.get_attribute('outerHTML')
        
        # Now use BeautifulSoup to extract content more precisely
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove obviously non-content elements
        for selector in [
            '.share-bar', '.sidebar', '.related-content', '.advertisement', 
            '.promotion', '.footer', '.author-footer', '.newsletter-signup',
            '.social-icons', 'nav', 'header', 'footer', 'script', 'style',
            'noscript', 'aside', '.comments'
        ]:
            for element in soup.select(selector):
                element.extract()
        
        # Extract text paragraphs, headings, and list items
        content_elements = soup.select('p, h1, h2, h3, h4, h5, h6, li, blockquote')
        
        # Reconstruct content hierarchically
        structured_content = []
        for element in content_elements:
            text = element.get_text(strip=True)
            
            # Skip empty elements and very short likely non-content elements
            if not text or (len(text) < 4 and element.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                continue
                
            # Skip likely navigation or utility text
            skip_phrases = ['back to top', 'read more', 'next article', 'related articles']
            if any(phrase in text.lower() for phrase in skip_phrases):
                continue
            
            # Format content based on element type
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                structured_content.append(f"\n\n{text}\n")
            elif element.name == 'blockquote':
                structured_content.append(f"\n\"{text}\"\n")
            elif element.name == 'li':
                structured_content.append(f"\n• {text}")
            else:
                structured_content.append(f"{text}")
        
        # Join structured content with appropriate spacing
        full_content = " ".join(structured_content)
        
        # Fix common spacing issues without regex
        full_content = full_content.replace("  ", " ")  # Double spaces
        full_content = full_content.replace(" .", ".")  # Space before period
        full_content = full_content.replace(" ,", ",")  # Space before comma
        
        # Extract metadata
        author_name = ""
        publication_date = ""
        
        # Try to find author
        author_selectors = [
            ".author-name", 
            ".byline", 
            "[data-test='author']", 
            ".author-bio", 
            ".contributor",
            ".article-meta-author"
        ]
        
        for selector in author_selectors:
            author_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if author_elements and len(author_elements) > 0:
                author_name = author_elements[0].text.strip()
                if author_name and len(author_name) > 1:
                    break
        
        # Try to find publication date
        date_selectors = [
            ".article-date", 
            ".publication-date", 
            ".date", 
            ".timestamp",
            "time",
            ".article-meta-date"
        ]
        
        for selector in date_selectors:
            date_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if date_elements and len(date_elements) > 0:
                publication_date = date_elements[0].text.strip()
                if publication_date and len(publication_date) > 1:
                    break
        
        # Create metadata
        metadata = {
            "title": title,
            "author": author_name,
            "publication_date": publication_date,
            "word_count": len(full_content.split()),
            "source": driver.current_url
        }
        
        return {
            "content": full_content,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"Error extracting content: {e}")
        return {
            "content": f"ERROR: Failed to extract content: {str(e)}",
            "metadata": {"error": str(e)}
        }

def handle_cookie_consent(driver):
    """
    Handle cookie consent dialogs on McKinsey pages.
    
    Args:
        driver: WebDriver instance
        
    Returns:
        bool: True if cookie dialog was handled, False otherwise
    """
    try:
        # Look for various cookie consent buttons and click them
        for selector in [
            "button#onetrust-accept-btn-handler",           # Most common McKinsey cookie button
            ".cookie-banner__button",                        # Alternative class
            "#truste-consent-button",                        # TrustArc consent
            "button.accept-cookies-button",                  # Generic accept button
            ".cookie-consent-accept",                        # Another common pattern
            "button[aria-label='Accept cookies']",           # Aria-labeled button
            "button[aria-label='Accept all cookies']",       # Alternative aria label
            ".accept-cookies"                                # Simple class name
        ]:
            try:
                # Short wait to check for each selector
                cookie_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                logger.info(f"Found cookie consent button: {selector}")
                cookie_button.click()
                # Give the page time to process after clicking
                time.sleep(2)
                return True
            except (TimeoutException, NoSuchElementException):
                # This selector didn't match, try the next one
                continue
                
        # If we got here, we didn't find any cookie buttons
        return False
                
    except Exception as e:
        logger.warning(f"Error handling cookie consent: {e}")
        return False

def scrape_article_content(driver, limit=None):
    """
    Scrape content for articles.
    
    Args:
        driver: WebDriver instance to use for scraping
        limit: Maximum number of articles to scrape
        
    Returns:
        Number of articles successfully scraped
    """
    try:
        # If driver creation failed, exit early
        if driver is None:
            logger.error("Invalid WebDriver for article scraping")
            return 0
            
        # Get the articles to scrape
        articles = get_unscrapped_articles(limit)
            
        if not articles:
            logger.info("No articles to scrape")
            return 0
            
        articles_scraped = 0
        failures = 0
        max_failures = 3
        
        logger.info(f"Starting to scrape content for {len(articles)} articles")
        
        for article in articles:
            try:
                # Skip articles with invalid URLs
                if not article.url or "{{" in article.url or "}}" in article.url:
                    logger.warning(f"Skipping article with invalid URL: {article.url}")
                    continue
                
                logger.info(f"Scraping content for article: {article.title}")
                
                # Load the article page
                driver.get(article.url)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Handle cookie consent
                cookie_handled = handle_cookie_consent(driver)
                if cookie_handled:
                    logger.info("Cookie consent handled successfully")
                    # Wait a bit longer for content to load after consent
                    time.sleep(2)
                
                # Get page content
                html_content = driver.page_source
                
                # Extract article content
                result = extract_content_from_dom(driver)
                
                # Store the article content
                success = store_article_content(
                    article,
                    article.url,
                    html_content,
                    result["content"],
                    result["metadata"]
                )
                
                if success:
                    articles_scraped += 1
                    logger.info(f"Successfully processed article: {article.title}")
                    failures = 0  # Reset failure counter after success
                
                # Add a small delay between articles
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"Error scraping content for article {article.url}: {e}")
                failures += 1
                
                if failures >= max_failures:
                    logger.warning(f"Too many consecutive failures ({failures}). Adding longer delay.")
                    time.sleep(random.uniform(20, 30))
                    failures = 0
        
        return articles_scraped
        
    except Exception as e:
        logger.error(f"Error in scrape_article_content: {e}")
        return 0

def scrape_all_unscrapped_articles(limit=None):
    """
    Scrape content for all articles that haven't been scrapped yet.
    
    Args:
        limit: Maximum number of articles to process
    
    Returns:
        Number of articles successfully scraped
    """
    try:
        # Ensure database exists
        engine = create_article_content_database()
        
        # Get article URLs that haven't been scrapped yet
        articles = get_unscrapped_articles()
        
        # Filter out invalid URLs
        valid_articles = []
        for article in articles:
            if not article.url or "{{" in article.url or "}}" in article.url:
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
        
        # Create a WebDriver for scraping
        driver = create_webdriver()
        if not driver:
            logger.error("Failed to create WebDriver")
            return 0
            
        try:
            # Scrape content for valid articles
            success_count = scrape_article_content(driver, valid_articles)
            
            logger.info(f"Content scraping complete. Successfully processed {success_count} articles.")
            return success_count
        finally:
            # Always close the driver
            if driver:
                driver.quit()
                logger.info("WebDriver closed")
        
    except Exception as e:
        logger.error(f"Error in scrape_all_unscrapped_articles: {e}")
        return 0

def export_content_to_csv(filename):
    """
    Export article content to a CSV file.
    
    Args:
        filename: Path to the output CSV file
        
    Returns:
        Number of articles exported
    """
    try:
        # Get database session
        session = get_session()
        
        # Query all article contents
        contents = session.query(ArticleContent).all()
        
        if not contents:
            logger.info("No article contents to export")
            return 0
            
        # Write to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Define CSV headers to match expected format
            fieldnames = ['article_id', 'title', 'url', 'content', 'author', 
                         'published_date', 'word_count', 'scraped_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for content in contents:
                # Parse metadata if available
                metadata = {}
                if content.article_metadata:
                    try:
                        metadata = json.loads(content.article_metadata)
                    except:
                        pass
                
                # Calculate word count from the content
                word_count = len(content.full_content.split()) if content.full_content else 0
                
                # Format data for CSV
                writer.writerow({
                    'article_id': content.article_id,
                    'title': content.title,
                    'url': content.url,
                    'content': content.full_content,
                    'author': metadata.get('author', ''),
                    'published_date': metadata.get('publication_date', ''),
                    'word_count': word_count,  # Use calculated word count
                    'scraped_at': content.scraped_at
                })
        
        logger.info(f"Successfully exported {len(contents)} articles to {filename}")
        session.close()
        return len(contents)
        
    except Exception as e:
        logger.error(f"Error exporting content to CSV: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 0

if __name__ == "__main__":
    # If run directly, scrape a small batch of articles
    logger.info("Starting article content scraper")
    count = scrape_all_unscrapped_articles(limit=5)
    logger.info(f"Completed scraping {count} articles") 