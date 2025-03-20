"""
Article content parser for McKinsey articles previously scraped.
"""

import time
import sqlite3
import argparse
import sys
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import traceback
import os
from concurrent.futures import ThreadPoolExecutor
import math

# Import utilities
from cookie_handler import handle_cookies

def setup_databases():
    """Connect to the existing SQLite database and create a new one for content if needed."""
    # Connect to the original database
    source_conn = sqlite3.connect('mckinsey_articles.db', check_same_thread=False)
    
    # Create or connect to content database
    content_db_path = 'mckinsey_article_content.db'
    
    # Check if database exists
    db_exists = os.path.exists(content_db_path)
    
    # Connect to the content database (creates it if it doesn't exist)
    content_conn = sqlite3.connect(content_db_path, check_same_thread=False)
    cursor = content_conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS article_content (
        article_id INTEGER PRIMARY KEY,
        title TEXT,
        authors TEXT,
        date TEXT,
        url TEXT,
        page_number INTEGER,
        content TEXT
    )
    ''')
    content_conn.commit()
    
    if db_exists:
        print(f"Connected to existing content database: {content_db_path}", flush=True)
        
        # Count existing articles
        cursor.execute("SELECT COUNT(*) FROM article_content")
        count = cursor.fetchone()[0]
        print(f"Found {count} articles in existing content database", flush=True)
    else:
        print(f"Created new content database: {content_db_path}", flush=True)
    
    return source_conn, content_conn

def get_unprocessed_articles(source_conn, content_conn, limit=None):
    """Get articles that haven't been processed yet."""
    content_cursor = content_conn.cursor()
    
    # Get IDs of already processed articles
    content_cursor.execute("SELECT article_id FROM article_content")
    processed_ids = [row[0] for row in content_cursor.fetchall()]
    
    # Create placeholders for the NOT IN query if we have processed articles
    if processed_ids:
        placeholders = ','.join(['?'] * len(processed_ids))
        query = f"SELECT id, title, authors, date, url, page_number FROM articles WHERE id NOT IN ({placeholders})"
        params = processed_ids
    else:
        query = "SELECT id, title, authors, date, url, page_number FROM articles"
        params = []
    
    # Add limit if specified
    if limit:
        query += f" LIMIT {limit}"
    
    # Execute query
    source_cursor = source_conn.cursor()
    source_cursor.execute(query, params)
    
    articles = source_cursor.fetchall()
    print(f"Found {len(articles)} unprocessed articles out of {len(processed_ids)} total processed", flush=True)
    
    return articles

def save_article_content(conn, article_id, title, authors, date, url, page_number, content):
    """Save article content to the new database."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO article_content (article_id, title, authors, date, url, page_number, content) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (article_id, title, authors, date, url, page_number, content)
    )
    conn.commit()
    print(f"[OK] Saved article ID {article_id} to database", flush=True)

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

def initialize_driver():
    """Initialize a new WebDriver with stealth settings."""
    chrome_options = configure_webdriver()
    driver = webdriver.Chrome(options=chrome_options)
    
    # Inject stealth script
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })
    
    # Initial visit to handle cookies once
    driver.get("https://www.mckinsey.com")
    handle_cookies(driver)
    
    return driver

def scroll_page(driver):
    """Scroll the page to load all content, but faster."""
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    
    # Use larger scroll steps - full viewport instead of half
    scroll_step = viewport_height  
    
    # Reduce the number of scrolls by using fewer steps
    num_steps = 4  # Fixed number of scroll positions
    scroll_positions = [i * (total_height / num_steps) for i in range(1, num_steps+1)]
    
    for position in scroll_positions:
        driver.execute_script(f"window.scrollTo(0, {position});")
        # Shorter delay between scrolls
        time.sleep(0.2)  
    
    # Final scroll to bottom to ensure everything is loaded
    driver.execute_script(f"window.scrollTo(0, {total_height});")
    time.sleep(0.3)
    
    # Scroll back to top
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.2)

def extract_article_content(driver, url):
    """Extract text content from article page."""
    print(f"Extracting content from: {url}", flush=True)
    
    try:
        driver.get(url)
        time.sleep(random.uniform(2, 3))  # Allow page to load
        
        # Scroll the page to ensure all content is loaded
        scroll_page(driver)
        
        # Selectors to try for article content (in priority order)
        content_selectors = [
            "article .body-content", 
            "article .article-body",
            "main article",
            ".article-content",
            ".content-wrapper",
            ".article",
            "#article-content"
        ]
        
        article_text = ""
        
        # Try each selector
        for selector in content_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # Use the first matching element
                    article_text = elements[0].text
                    break
            except Exception:
                continue
        
        # If no specific selector worked, grab all paragraph text
        if not article_text:
            paragraphs = driver.find_elements(By.TAG_NAME, "p")
            article_text = "\n\n".join([p.text for p in paragraphs if p.text.strip()])
        
        if article_text:
            print(f"Successfully extracted {len(article_text)} characters of text", flush=True)
            return article_text
        else:
            print("No content found", flush=True)
            return "No content could be extracted"
    
    except Exception as e:
        print(f"Error extracting content: {str(e)}", flush=True)
        traceback.print_exc()
        return f"Error: {str(e)}"

def worker_process(worker_id, articles, content_conn, verbose=False):
    """Process a subset of articles in a worker thread."""
    print(f"Worker {worker_id}: Starting with {len(articles)} articles to process", flush=True)
    
    # Initialize a new driver for this worker
    driver = initialize_driver()
    results = []
    
    try:
        for idx, (article_id, title, authors, date, url, page_number) in enumerate(articles, 1):
            article_result = {
                "article_id": article_id,
                "title": title,
                "status": "pending"
            }
            
            try:
                if verbose:
                    print(f"Worker {worker_id}: [{idx}/{len(articles)}] Processing article: {title}", flush=True)
                else:
                    print(f"Worker {worker_id}: Processing article ID {article_id}", flush=True)
                
                # Extract content
                content = extract_article_content(driver, url)
                
                # Save to database
                save_article_content(content_conn, article_id, title, authors, date, url, page_number, content)
                
                article_result["status"] = "success"
                
                # Random delay between articles
                if idx < len(articles):
                    delay = random.uniform(1, 2)
                    if verbose:
                        print(f"Worker {worker_id}: Waiting {delay:.1f} seconds before next article...", flush=True)
                    time.sleep(delay)
                
            except Exception as e:
                print(f"Worker {worker_id}: Error processing article {article_id}: {str(e)}", flush=True)
                if verbose:
                    traceback.print_exc()
                article_result["status"] = "error"
                article_result["error"] = str(e)
            
            results.append(article_result)
    
    finally:
        # Always close the driver
        driver.quit()
        print(f"Worker {worker_id}: Finished processing {len(articles)} articles", flush=True)
    
    return results

def divide_articles(articles, num_workers):
    """Divide articles among workers."""
    if not articles:
        return []
    
    total_articles = len(articles)
    
    # If we have more workers than articles, limit workers
    actual_workers = min(num_workers, total_articles)
    
    # Calculate articles per worker
    articles_per_worker = math.ceil(total_articles / actual_workers)
    
    # Divide articles among workers
    article_assignments = []
    for i in range(actual_workers):
        start_idx = i * articles_per_worker
        end_idx = min(start_idx + articles_per_worker, total_articles)
        if start_idx < total_articles:
            article_assignments.append(articles[start_idx:end_idx])
    
    return article_assignments

def process_articles(limit=None, max_workers=1, verbose=False):
    """Process articles from the database."""
    source_conn, content_conn = setup_databases()
    
    try:
        # Get articles to process
        articles = get_unprocessed_articles(source_conn, content_conn, limit)
        total_articles = len(articles)
        
        if total_articles == 0:
            print("No articles found to process", flush=True)
            return
        
        print(f"Found {total_articles} articles to process", flush=True)
        
        # Single-threaded mode
        if max_workers == 1:
            print("Running in single-threaded mode", flush=True)
            
            # Initialize driver once
            driver = initialize_driver()
            
            try:
                # Process each article
                processed_count = 0
                for idx, (article_id, title, authors, date, url, page_number) in enumerate(articles, 1):
                    print(f"\n[{idx}/{total_articles}] Processing article: {title}", flush=True)
                    
                    try:
                        # Extract content
                        content = extract_article_content(driver, url)
                        
                        # Save to new database with all metadata
                        save_article_content(content_conn, article_id, title, authors, date, url, page_number, content)
                        
                        # Explicitly commit again to ensure data is saved
                        content_conn.commit()
                        
                        processed_count += 1
                        
                        # Random delay between articles
                        if idx < total_articles:
                            delay = random.uniform(1.5, 3)
                            print(f"Waiting {delay:.1f} seconds before next article...", flush=True)
                            time.sleep(delay)
                    
                    except Exception as e:
                        print(f"Error processing article {article_id}: {str(e)}", flush=True)
                        traceback.print_exc()
                
                print(f"\nCompleted processing {processed_count} out of {total_articles} articles", flush=True)
                
            finally:
                # Always close the driver
                driver.quit()
                print("WebDriver closed", flush=True)
        
        # Multi-threaded mode
        else:
            print(f"Running in multi-threaded mode with {max_workers} workers", flush=True)
            
            # Divide articles among workers
            article_assignments = divide_articles(articles, max_workers)
            actual_workers = len(article_assignments)
            
            print(f"Using {actual_workers} workers for {total_articles} articles", flush=True)
            
            all_results = []
            
            # Create thread pool
            with ThreadPoolExecutor(max_workers=actual_workers) as executor:
                # Submit worker tasks
                future_to_worker = {
                    executor.submit(worker_process, i+1, article_batch, content_conn, verbose): i+1 
                    for i, article_batch in enumerate(article_assignments)
                }
                
                # Process results
                for future in future_to_worker:
                    worker_id = future_to_worker[future]
                    try:
                        worker_results = future.result()
                        all_results.extend(worker_results)
                        successful = sum(1 for r in worker_results if r['status'] == 'success')
                        print(f"Worker {worker_id} completed with {successful} successful articles", flush=True)
                    except Exception as e:
                        print(f"Worker {worker_id} failed: {str(e)}", flush=True)
                        if verbose:
                            traceback.print_exc()
            
            # Print summary
            successful = sum(1 for r in all_results if r['status'] == 'success')
            errors = sum(1 for r in all_results if r['status'] == 'error')
            
            print("\n===== PARSING SUMMARY =====", flush=True)
            print(f"Total articles processed: {len(all_results)}", flush=True)
            print(f"Successful: {successful}", flush=True)
            print(f"Errors: {errors}", flush=True)
            print("===========================", flush=True)
    
    finally:
        source_conn.close()
        content_conn.close()
        print("Database connections closed", flush=True)

def main():
    """Main function to parse article content."""
    parser = argparse.ArgumentParser(description='Parse McKinsey article content.')
    parser.add_argument('-l', '--limit', type=int, help='Limit number of articles to process')
    parser.add_argument('-w', '--workers', type=int, default=1, help='Number of concurrent workers')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()
    
    try:
        process_articles(limit=args.limit, max_workers=args.workers, verbose=args.verbose)
        print("Article parsing completed successfully!", flush=True)
    except Exception as e:
        print(f"Error during article parsing: {str(e)}", file=sys.stderr, flush=True)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 