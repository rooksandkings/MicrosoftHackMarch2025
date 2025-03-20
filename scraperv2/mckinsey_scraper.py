"""
McKinsey scraper for extracting article information from search results.
"""

import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import argparse
import sys

# Import utilities
from cookie_handler import handle_cookies
from link_extractor import extract_article_links, extract_authors, extract_date

def setup_database():
    """Set up SQLite database for storing articles."""
    conn = sqlite3.connect('mckinsey_articles.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        authors TEXT,
        date TEXT,
        url TEXT UNIQUE,
        page_number INTEGER
    )
    ''')
    conn.commit()
    return conn

def save_to_database(conn, articles):
    """Save articles to database."""
    print(f"Saving {len(articles)} articles to database...", flush=True)
    cursor = conn.cursor()
    
    inserted_count = 0
    duplicate_count = 0
    
    for article in articles:
        try:
            cursor.execute(
                "INSERT INTO articles (title, authors, date, url, page_number) VALUES (?, ?, ?, ?, ?)",
                (article['title'], article['authors'], article['date'], article['url'], article['page_number'])
            )
            inserted_count += 1
        except sqlite3.IntegrityError:
            duplicate_count += 1
    
    conn.commit()
    print(f"Database update: {inserted_count} articles inserted, {duplicate_count} duplicates skipped", flush=True)

def configure_webdriver():
    """Configure Chrome WebDriver with anti-detection measures."""
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
    chrome_options.add_argument("--window-size=1920,1080")
    
    return chrome_options

def scrape_page(page_number, shared_driver=None):
    """Scrape McKinsey search results for a specific page."""
    print(f"Starting scrape for page {page_number}", flush=True)
    
    chrome_options = configure_webdriver()
    
    # Create a new driver if not provided
    close_driver = False
    if shared_driver is None:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Inject stealth script
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })
        close_driver = True
    else:
        driver = shared_driver
    
    current_url = driver.current_url
    print(f"Scraping URL: {current_url}", flush=True)
    
    try:
        # Try finding article containers with various selectors
        selectors = [
            ".search-result", 
            "article.result-card",
            ".search-results-container .result",
            "[data-test='search-results'] article",
            ".search-results-list li",
            "main article"
        ]
        
        articles_data = []
        found_container = False
        
        # Try to find article containers with selectors
        for selector in selectors:
            articles = driver.find_elements(By.CSS_SELECTOR, selector)
            if articles:
                found_container = True
                print(f"Found {len(articles)} articles with selector: {selector}", flush=True)
                
                # Process each article container
                for idx, article in enumerate(articles[:10], 1):
                    try:
                        # Find title and URL
                        title_element = None
                        title_selectors = ["h2 a", "h3 a", "h4 a", ".title a", "a.title"]
                        
                        for title_selector in title_selectors:
                            try:
                                title_element = article.find_element(By.CSS_SELECTOR, title_selector)
                                break
                            except:
                                continue
                        
                        if not title_element:
                            try:
                                title_element = article.find_element(By.TAG_NAME, "a")
                            except:
                                continue
                        
                        title = title_element.text.strip()
                        url = title_element.get_attribute("href")
                        
                        # Skip navigation links and empty titles
                        if len(title) < 5 or title.lower() in ["next", "previous"]:
                            continue
                        
                        # Extract metadata
                        authors = extract_authors(article)
                        date = extract_date(article)
                        
                        articles_data.append({
                            "title": title,
                            "authors": authors,
                            "date": date,
                            "url": url,
                            "page_number": page_number
                        })
                        
                        # Limit to 10 articles
                        if len(articles_data) >= 10:
                            break
                            
                    except Exception as e:
                        print(f"Error extracting article data: {str(e)}", flush=True)
                
                # If we found and processed articles, break out of selector loop
                if articles_data:
                    break
        
        # If no articles found with selectors, try direct link extraction
        if not found_container or not articles_data:
            print("Using direct link extraction method", flush=True)
            articles_data = extract_article_links(driver, page_number)
        
        print(f"Completed scraping page {page_number}, found {len(articles_data)} articles", flush=True)
        return articles_data[:10]
        
    except Exception as e:
        print(f"Error scraping page {page_number}: {str(e)}", flush=True)
        return []
        
    finally:
        if close_driver:
            driver.quit()

def main(start_page=1, end_page=1, max_workers=1, verbose=False):
    """Main function to run the scraper."""
    print(f"Starting McKinsey scraper on page {start_page}", flush=True)
    
    # Set up database
    conn = setup_database()
    
    # Configure and initialize WebDriver
    chrome_options = configure_webdriver()
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })
    
    try:
        # Construct search URL
        search_url = f"https://www.mckinsey.com/search?q=change+management&pageFilter=all&sort=default"
        if start_page > 1:
            search_url += f"&start={start_page}"
        
        print(f"Navigating to: {search_url}", flush=True)
        driver.get(search_url)
        
        # Handle cookies if they appear
        handle_cookies(driver)
        
        # Process the page
        result = scrape_page(start_page, driver)
        
        # Save results
        save_to_database(conn, result)
        
        print(f"Scraping summary: Found {len(result)} articles on page {start_page}", flush=True)
    
    finally:
        driver.quit()
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape McKinsey articles.')
    parser.add_argument('-s', '--start-page', type=int, default=1, help='Starting page number')
    parser.add_argument('-e', '--end-page', type=int, default=1, help='Ending page number')
    parser.add_argument('-w', '--workers', type=int, default=1, help='Number of concurrent workers')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()
    
    try:
        main(start_page=args.start_page, end_page=args.end_page, 
             max_workers=args.workers, verbose=args.verbose)
        print("Scraping completed successfully!", flush=True)
    except Exception as e:
        print(f"Error during scraping: {str(e)}", file=sys.stderr, flush=True)
        sys.exit(1) 