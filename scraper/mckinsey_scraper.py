"""
McKinsey Search Results Scraper

This script scrapes search results from McKinsey's website and stores them in an SQL database.
It uses Selenium WebDriver to render JavaScript content before scraping.
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
import threading
from queue import Queue

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# Update import at the top:
from database_utils import store_article, get_session, Article

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


def create_webdriver():
    """
    Create and configure a WebDriver instance, using Edge or Firefox only.
    
    Returns:
        WebDriver: Configured WebDriver instance
    """
    user_agent = get_user_agent()
    
    # Common options for browsers
    common_args = [
        "--headless",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        f"user-agent={user_agent}",
        "--disable-notifications",
        "--disable-popup-blocking", 
        "--disable-extensions"
    ]
    
    # Start with Edge which is already working
    try:
        logger.info("Creating Edge WebDriver")
        from selenium.webdriver.edge.service import Service as EdgeService
        from selenium.webdriver.edge.options import Options as EdgeOptions
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        
        edge_options = EdgeOptions()
        for arg in common_args:
            edge_options.add_argument(arg)
        
        edge_service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=edge_service, options=edge_options)
        driver.set_page_load_timeout(30)
        logger.info("Successfully created Edge WebDriver")
        return driver
    except Exception as e:
        logger.warning(f"Edge WebDriver creation failed: {e}")
    
    # Try Firefox as fallback
    try:
        logger.info("Creating Firefox WebDriver")
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from webdriver_manager.firefox import GeckoDriverManager
        
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")
        
        # Set user agent for Firefox
        firefox_options.set_preference("general.useragent.override", user_agent)
        
        firefox_service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=firefox_service, options=firefox_options)
        driver.set_page_load_timeout(30)
        logger.info("Successfully created Firefox WebDriver")
        return driver
    except Exception as e:
        logger.warning(f"Firefox WebDriver creation failed: {e}")
    
    # If we get here, no WebDriver could be created
    logger.error("No WebDriver could be created. Please ensure Edge or Firefox is installed.")
    return None


def fetch_page_with_selenium(url, params=None):
    """
    Fetch a page using Selenium to allow JavaScript to execute.
    
    Args:
        url (str): Base URL
        params (dict, optional): URL parameters
        
    Returns:
        tuple: (WebDriver, HTML content)
    """
    driver = None
    try:
        # Build the full URL with parameters
        full_url = url
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{query_string}"
        
        logger.info(f"Fetching {full_url} with Selenium")
        
        # Create a WebDriver
        driver = create_webdriver()
        if not driver:
            logger.error("Failed to create WebDriver")
            return None, None
        
        # Navigate to the URL
        driver.get(full_url)
        
        # Handle cookie popup
        try:
            logger.info("Checking for cookie consent popup...")
            # Wait for cookie popup with various possible selectors
            cookie_button_selectors = [
                "button.accept-cookies-button",
                "button.accept-all-cookies",
                "button.accept_all",
                "button[id*='cookie'][id*='accept']",
                "button[class*='cookie'][class*='accept']",
                "button[aria-label*='Accept']",
                "button[aria-label*='accept all']",
                "button[data-test-id*='accept-all']",
                ".cookie-banner .accept",
                "#onetrust-accept-btn-handler",
                "#accept-all-cookies",
                "#truste-consent-button",
                "[aria-label='Accept cookies']",
                "button:contains('Accept All')",
                "[class*='cookieConsent'] button:contains('Accept')"
            ]
            
            # Try each selector until one works
            for selector in cookie_button_selectors:
                try:
                    WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    cookie_button = driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"Found cookie consent button with selector: {selector}")
                    cookie_button.click()
                    logger.info("Clicked cookie consent button")
                    time.sleep(1)  # Wait a moment for the popup to disappear
                    break
                except:
                    continue
                    
            # Alternative approach for complex cookie dialogs
            try:
                # Try to find buttons by text
                buttons = driver.find_elements(By.TAG_NAME, "button")
                accept_texts = ["accept all", "accept cookies", "i accept", "agree", "ok"]
                
                for button in buttons:
                    button_text = button.text.lower()
                    if any(accept_text in button_text for accept_text in accept_texts):
                        logger.info(f"Found cookie button by text: {button.text}")
                        button.click()
                        logger.info("Clicked cookie consent button by text")
                        time.sleep(1)
                        break
            except Exception as e:
                logger.warning(f"Failed to click cookie button by text: {e}")
                
        except Exception as e:
            logger.warning(f"Error handling cookie popup: {e}")
        
        logger.info("Waiting for page to load and JavaScript to execute...")
        try:
            # Wait for initial page load
            time.sleep(5)  # Initial wait for JavaScript to start
            
            # Wait for the search results to appear
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results, .results, .items"))
            )
            
            # Check if we see template placeholders
            html = driver.page_source
            if "{{" in html and "}}" in html:
                logger.info("Detected template placeholders, waiting for actual content...")
                # Wait longer for JavaScript to replace templates
                for i in range(10):
                    time.sleep(2)
                    html = driver.page_source
                    if "{{" not in html:
                        logger.info("Templates have been replaced with actual content.")
                        break
            
            # Get page title for debugging
            logger.info(f"Page title: {driver.title}")
            
            # Save final HTML for debugging
            with open('mckinsey_search_debug.html', 'w', encoding='utf-8') as f:
                f.write(html)
            
            return driver, html
            
        except Exception as e:
            logger.warning(f"Error waiting for page load: {e}")
            
            # Still try to return what we have
            if driver:
                return driver, driver.page_source
            return None, None
            
    except Exception as e:
        logger.error(f"Error in fetch_page_with_selenium: {e}")
        if driver:
            try:
                driver.quit()
            except:
                pass
        return None, None


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
    
    logger.info("Analyzing search results page structure")
    
    # Check if the page has template placeholders that haven't been replaced
    if "{{" in html_content and "}}" in html_content:
        logger.warning("Page contains unreplaced template placeholders. JavaScript may not have executed fully.")
    
    # Log the entire HTML to a file for debugging
    with open("mckinsey_search_debug.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info("Wrote HTML to mckinsey_search_debug.html for debugging")
    
    # Try various selectors based on common article patterns
    # This is a broad approach to catch whatever structure is being used
    search_selectors = [
        'article', '.search-result', '.result-item', '.card', 
        'div[role="article"]', '.tile', '.article-preview',
        'li.listing', '.list-item', '.item', '.hit', '.result'
    ]
    
    for selector in search_selectors:
        search_results = soup.select(selector)
        if search_results:
            logger.info(f"Found {len(search_results)} results with selector '{selector}'")
            break
    else:
        search_results = []
        logger.warning("No search results found with any selector")
    
    if not search_results:
        # As a fallback, look for any links that might be search results
        all_links = soup.find_all('a', href=True)
        insightful_links = [link for link in all_links if '/insights/' in link.get('href', '')]
        
        if insightful_links:
            logger.info(f"Found {len(insightful_links)} possible links to insights as fallback")
            
            for link in insightful_links:
                try:
                    url = link['href']
                    if not url.startswith('http'):
                        url = "https://www.mckinsey.com" + (url if url.startswith('/') else '/' + url)
                    
                    title = link.get_text().strip() or "No title"
                    
                    if url and '/insights/' in url:  # Only add if we have a URL to an insight
                        article = {
                            'title': title,
                            'url': url,
                            'description': "",
                            'date_published': "",
                            'article_type': "Article",
                        }
                        
                        articles.append(article)
                        logger.info(f"Parsed article: {title} - {url}")
                except Exception as e:
                    logger.error(f"Error parsing fallback link: {e}")
    
    # If we found actual search results, process them normally
    for result in search_results:
        try:
            # Look for any link within the result element
            link_elem = result.find('a', href=True)
            if not link_elem:
                continue
                
            url = link_elem['href']
            
            # Skip URLs with template placeholders
            if "{{" in url or "}}" in url:
                logger.warning(f"Skipping URL with template placeholders: {url}")
                continue
                
            if not url.startswith('http'):
                url = "https://www.mckinsey.com" + (url if url.startswith('/') else '/' + url)
            
            # Get title from link text or any heading inside the result
            title_elem = result.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']) or link_elem
            title = title_elem.get_text().strip() if title_elem else "No title"
            
            # Look for any paragraph that might be a description
            description_elem = result.find('p')
            description = description_elem.get_text().strip() if description_elem else ""
            
            # Look for any date-like text
            date_published = ""
            date_patterns = [r'\b\d{1,2}\s+\w+\s+\d{4}\b', r'\b\w+\s+\d{1,2},\s+\d{4}\b']
            for pattern in date_patterns:
                import re
                date_match = re.search(pattern, result.get_text())
                if date_match:
                    date_published = date_match.group(0)
                    break
            
            if url:  # Only add if we have a URL
                article = {
                    'title': title,
                    'url': url,
                    'description': description,
                    'date_published': date_published,
                    'article_type': "Article",  # Default type
                }
                
                articles.append(article)
                logger.info(f"Parsed article: {title} - {url}")
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
    
    logger.info(f"Found {len(articles)} articles in search results")
    return articles


def get_article_content_with_selenium(url):
    """
    Get the full content of an article using Selenium to render JavaScript.
    
    Args:
        url (str): Article URL
        
    Returns:
        tuple: (title, content text) or (None, None) if failed
    """
    driver = create_webdriver()
    if not driver:
        return None, None
    
    try:
        logger.info(f"Fetching article content from {url}")
        driver.get(url)
        
        # Wait for article content to load
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article, .article, .content"))
            )
        except TimeoutException:
            logger.warning(f"Timeout waiting for article content on {url}")
        
        # Get title
        try:
            title = driver.title
        except:
            title = "Unknown Title"
        
        # Get content
        try:
            # Try different selectors for article content
            content_elem = driver.find_element(By.CSS_SELECTOR, "article, .article, .content, main")
            content = content_elem.text
        except:
            content = "Failed to extract content"
        
        return title, content
    
    except Exception as e:
        logger.error(f"Error fetching article content from {url}: {e}")
        return None, None
    
    finally:
        driver.quit()


def store_articles(articles):
    """
    Store articles in the database.
    
    Args:
        articles (list): List of article dictionaries
        
    Returns:
        int: Number of new articles stored
    """
    try:
        # Create database and tables if they don't exist
        create_database()
        
        new_articles = 0
        for article in articles:
            # Skip articles with template placeholders
            if "{{" in article['url'] or "}}" in article['url']:
                logger.warning(f"Skipping article with invalid URL: {article['url']}")
                continue
                
            # Check if the article already exists
            with get_session() as session:
                existing = session.query(Article).filter(Article.url == article['url']).first()
                if existing:
                    # logger.debug(f"Article already exists: {article['title']}")
                    continue
                    
                # Create a new article
                new_article = Article(
                    title=article['title'],
                    url=article['url'],
                    description=article.get('description', ''),
                    date_published=article.get('date_published', None),
                    article_type=article.get('article_type', '')
                )
                
                session.add(new_article)
                new_articles += 1
        
        logger.info(f"Stored {new_articles} new articles in the database")
        return new_articles
        
    except Exception as e:
        logger.error(f"Error storing articles: {e}")
        return 0


def get_total_results_and_pages(html_content):
    """
    Extract the total number of results and calculate pages from search results.
    
    Args:
        html_content (str): HTML content
        
    Returns:
        tuple: (total_results, total_pages)
    """
    if not html_content:
        return 0, 1
    
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Try to find the result count text which might be in various formats
    # Examples: "1-10 of 150 results" or "Showing 1-10 of about 150 results"
    result_count_text = None
    
    # Try different possible selectors for result count
    result_count_selectors = [
        '.search-results-count', 
        '.result-count', 
        '.search-header', 
        '.search-summary'
    ]
    
    for selector in result_count_selectors:
        count_elem = soup.select_one(selector)
        if count_elem:
            result_count_text = count_elem.text.strip()
            break
    
    # Default values if we can't find the information
    total_results = 0
    
    if result_count_text:
        # Try to extract total results from text using regex
        import re
        matches = re.search(r'of\s+(?:about\s+)?(\d+)', result_count_text)
        if matches:
            total_results = int(matches.group(1))
    
    # Calculate total pages (assuming 10 results per page)
    results_per_page = 10
    total_pages = (total_results + results_per_page - 1) // results_per_page
    
    # Fallback to at least 1 page
    total_pages = max(1, total_pages)
    
    logger.info(f"Found approximately {total_results} total results across {total_pages} pages")
    return total_results, total_pages


class ScrapeWorker(threading.Thread):
    """Worker thread that keeps a WebDriver alive for multiple tasks."""
    
    def __init__(self, task_queue, result_queue, worker_id):
        """
        Initialize a scrape worker.
        
        Args:
            task_queue (Queue): Queue of (query, page) tasks to process
            result_queue (Queue): Queue to store results
            worker_id (int): Unique ID for this worker
        """
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.worker_id = worker_id
        self.driver = None
        self.cookie_handled = False
        self.daemon = True  # Make threads daemon so they exit when main thread exits
        
    def run(self):
        """Process tasks from the queue until it's empty."""
        try:
            logger.info(f"Worker {self.worker_id} starting")
            
            # Create a WebDriver for this worker
            self.driver = create_webdriver()
            if not self.driver:
                logger.error(f"Worker {self.worker_id} failed to create WebDriver")
                return
                
            # Process tasks until the queue is empty
            while not self.task_queue.empty():
                try:
                    # Get a task from the queue with a timeout
                    query, page, results_per_page = self.task_queue.get(timeout=1)
                    
                    # Process the task
                    try:
                        self.scrape_page(query, page, results_per_page)
                    except Exception as e:
                        logger.error(f"Worker {self.worker_id} error scraping page {page}: {e}")
                    finally:
                        # Mark the task as done
                        self.task_queue.task_done()
                except Exception:
                    # Queue.get timeout or other issue
                    break
                    
        except Exception as e:
            logger.error(f"Worker {self.worker_id} encountered an error: {e}")
        finally:
            # Clean up resources with a timeout
            if self.driver:
                try:
                    # Use a more aggressive timeout for quitting
                    self.driver.set_page_load_timeout(2)
                    self.driver.set_script_timeout(2)
                    
                    # Start a timer for quitting
                    quit_start = time.time()
                    self.driver.quit()
                    quit_time = time.time() - quit_start
                    logger.info(f"Worker {self.worker_id} closed WebDriver in {quit_time:.2f}s")
                except Exception as e:
                    logger.warning(f"Worker {self.worker_id} failed to close WebDriver: {e}")
                    # Force close if quit fails
                    try:
                        self.driver.close()
                    except:
                        pass
                self.driver = None  # Release reference
    
    def scrape_page(self, query, page, results_per_page):
        """
        Scrape a single page of search results and store articles immediately.
        
        Args:
            query (str): Search query
            page (int): Page number to scrape
            results_per_page (int): Number of results per page
        """
        start_index = (page - 1) * results_per_page + 1
        
        logger.info(f"Worker {self.worker_id} scraping page {page} (start={start_index}) for query: {query}")
        
        # Set up the search parameters
        params = {
            "q": query,
            "pageFilter": "all",
            "sort": "default",
            "start": start_index
        }
        
        # Build the full URL with parameters
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{BASE_URL}?{query_string}"
        
        # Navigate to the search page
        self.driver.get(full_url)
        
        # Handle cookie popup if needed
        if not self.cookie_handled:
            try:
                # Use a short timeout for the cookie popup
                cookie_button_selectors = [
                    "#onetrust-accept-btn-handler",
                    "button.accept-cookies-button",
                    "button.accept-all-cookies"
                ]
                
                # Try each selector with a shorter timeout
                for selector in cookie_button_selectors:
                    try:
                        WebDriverWait(self.driver, 1).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        cookie_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        logger.info(f"Worker {self.worker_id} found cookie consent button")
                        cookie_button.click()
                        time.sleep(1)
                        self.cookie_handled = True
                        break
                    except Exception:
                        continue
            except Exception as e:
                logger.warning(f"Worker {self.worker_id} error handling cookie popup: {e}")
        
        # Wait for search results
        try:
            # Wait for any search result item to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".item, .search-result, .searchResult"))
            )
            
            # Wait for multiple results
            def has_multiple_results(driver):
                items = driver.find_elements(By.CSS_SELECTOR, ".item, .search-result, .searchResult")
                return len(items) >= 3
            
            WebDriverWait(self.driver, 5).until(has_multiple_results)
            logger.info(f"Worker {self.worker_id} search results loaded")
        except Exception as e:
            logger.warning(f"Worker {self.worker_id} timeout waiting for results: {e}")
        
        # Get page content
        html_content = self.driver.page_source
        
        # Check for template placeholders
        if "{{" in html_content and "}}" in html_content:
            logger.info(f"Worker {self.worker_id} waiting for templates to resolve...")
            
            max_wait_seconds = 8
            start_time = time.time()
            
            while time.time() - start_time < max_wait_seconds:
                time.sleep(0.5)
                html_content = self.driver.page_source
                if "{{" not in html_content:
                    break
        
        # Parse the search results
        articles = parse_articles(html_content)
        
        # Store articles immediately instead of just putting in queue
        if articles:
            logger.info(f"Worker {self.worker_id} found {len(articles)} articles on page {page}")
            
            # Store articles in database immediately
            new_articles = store_articles(articles)
            
            # Report success
            self.result_queue.put((page, new_articles))
            logger.info(f"Worker {self.worker_id} stored {new_articles} new articles from page {page}")
        else:
            logger.info(f"Worker {self.worker_id} no articles found on page {page}")
            self.result_queue.put((page, 0))

def scrape_mckinsey_search_parallel(query, test_mode=True, max_pages=5, max_workers=3):
    """
    Scrape McKinsey search results in parallel using persistent workers
    with immediate storage per page.
    
    Args:
        query (str): Search query
        test_mode (bool): If True, only scrape the first page
        max_pages (int): Maximum number of pages to scrape
        max_workers (int): Maximum number of parallel workers
        
    Returns:
        int: Number of articles stored
    """
    try:
        if test_mode:
            max_pages = 1
            
        # Adjust max_workers based on max_pages
        max_workers = min(max_workers, max_pages)
        
        logger.info(f"Starting parallel scraping for query '{query}' with {max_workers} workers")
        
        # Create task queue and result queue
        task_queue = Queue()
        result_queue = Queue()
        
        # Add tasks to the queue
        results_per_page = 10
        for page in range(1, max_pages + 1):
            task_queue.put((query, page, results_per_page))
            
        # Create and start worker threads
        workers = []
        for i in range(max_workers):
            worker = ScrapeWorker(task_queue, result_queue, i+1)
            workers.append(worker)
            worker.start()
            # Smaller delay between starting workers
            time.sleep(0.1)
            
        # Wait for all tasks to be processed with a timeout
        task_queue.join()
        
        # Wait for all workers to finish with a timeout
        for worker in workers:
            worker.join(timeout=3)  # Only wait max 3 seconds per worker
            
        # Calculate total articles stored
        total_articles = 0
        
        # Get results from the queue with a timeout
        start_time = time.time()
        max_wait_time = 3  # Max seconds to wait for queue processing
        
        while not result_queue.empty() and (time.time() - start_time < max_wait_time):
            try:
                page, new_articles = result_queue.get(timeout=0.5)
                total_articles += new_articles
            except:
                # Timeout on queue get
                break
            
        logger.info(f"All pages processed. Total new articles stored: {total_articles}")
        return total_articles
        
    except Exception as e:
        logger.error(f"Error in parallel scraping: {e}")
        return 0


if __name__ == "__main__":
    logger.info("Starting McKinsey search scraper with Selenium WebDriver")
    
    # Initial deployment - test mode (first page only)
    article_count = scrape_mckinsey_search_parallel(SEARCH_QUERY, test_mode=True)
    
    logger.info(f"Scraping completed. Stored {article_count} articles.") 