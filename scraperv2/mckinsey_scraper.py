"""
McKinsey scraper for extracting article information from search results.
"""

import time
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import argparse
import sys
import random
import math

# Import utilities
from cookie_handler import handle_cookies
from link_extractor import extract_article_links, extract_authors, extract_date

def setup_database():
    """Set up SQLite database for storing articles."""
    conn = sqlite3.connect('mckinsey_articles.db', check_same_thread=False)
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

def get_page_url(page_number):
    """Generate the URL for a specific page number."""
    base_url = "https://www.mckinsey.com/search?q=change+management&pageFilter=all&sort=default"
    if page_number > 1:
        return f"{base_url}&start={page_number}"
    return base_url

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
    
    # Clear storage to start fresh but keep the session
    driver.execute_script("localStorage.clear(); sessionStorage.clear();")
    
    return driver

def scrape_page(page_number, driver):
    """Scrape McKinsey search results for a specific page using provided driver."""
    print(f"Scraping page {page_number} with reused driver", flush=True)
    
    try:
        # Navigate to the specific page
        page_url = get_page_url(page_number)
        print(f"Navigating to URL: {page_url}", flush=True)
        driver.get(page_url)
        
        # Allow time for page to fully load
        time.sleep(random.uniform(1.5, 3))
        
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

def worker_process(worker_id, page_list, conn, verbose=False):
    """Worker function to process multiple pages with a single WebDriver."""
    print(f"Worker {worker_id} starting, assigned pages: {page_list}", flush=True)
    
    # Create a single WebDriver for this worker
    driver = initialize_driver()
    
    results = []
    
    try:
        for page_number in page_list:
            print(f"Worker {worker_id}: Processing page {page_number}", flush=True)
            
            # Scrape the page
            page_results = scrape_page(page_number, driver)
            
            # Save to database
            if page_results:
                save_to_database(conn, page_results)
                
            # Record results
            results.append({
                "page": page_number,
                "count": len(page_results),
                "status": "success" if page_results else "no_results"
            })
            
            # Random delay between pages (shorter since we're using the same session)
            if page_number != page_list[-1]:  # If not the last page
                sleep_time = random.uniform(1, 2.5)
                print(f"Worker {worker_id}: Waiting {sleep_time:.1f}s before next page...", flush=True)
                time.sleep(sleep_time)
        
        print(f"Worker {worker_id} completed all assigned pages", flush=True)
        return results
    
    except Exception as e:
        print(f"Worker {worker_id} encountered an error: {str(e)}", flush=True)
        return results
    
    finally:
        # Always close the driver
        try:
            driver.quit()
            print(f"Worker {worker_id}: WebDriver closed", flush=True)
        except:
            pass

def divide_pages(start_page, end_page, num_workers):
    """Divide pages among workers evenly."""
    pages = list(range(start_page, end_page + 1))
    total_pages = len(pages)
    
    # If we have more workers than pages, limit workers
    actual_workers = min(num_workers, total_pages)
    
    # Calculate pages per worker
    pages_per_worker = math.ceil(total_pages / actual_workers)
    
    # Divide pages among workers
    page_assignments = []
    for i in range(actual_workers):
        start_idx = i * pages_per_worker
        end_idx = min(start_idx + pages_per_worker, total_pages)
        if start_idx < total_pages:
            page_assignments.append(pages[start_idx:end_idx])
    
    return page_assignments

def main(start_page=1, end_page=1, max_workers=1, verbose=False):
    """Main function with efficient WebDriver reuse."""
    print(f"Starting McKinsey scraper with settings:", flush=True)
    print(f"  Start page: {start_page}", flush=True)
    print(f"  End page: {end_page}", flush=True)
    print(f"  Workers: {max_workers}", flush=True)
    
    # Set up database
    conn = setup_database()
    
    try:
        # Single-threaded mode
        if max_workers == 1 or start_page == end_page:
            print("Running in single-threaded mode", flush=True)
            
            # Initialize single driver
            driver = initialize_driver()
            
            try:
                results = []
                
                # Process each page
                for page in range(start_page, end_page + 1):
                    print(f"\n===== PROCESSING PAGE {page} =====", flush=True)
                    
                    # Scrape page
                    page_results = scrape_page(page, driver)
                    
                    # Save results
                    save_to_database(conn, page_results)
                    
                    results.append({
                        "page": page,
                        "count": len(page_results),
                        "status": "success" if page_results else "no_results"
                    })
                    
                    # Sleep between pages
                    if page < end_page:
                        sleep_time = random.uniform(1.5, 3)
                        print(f"Waiting {sleep_time:.1f} seconds before next page...", flush=True)
                        time.sleep(sleep_time)
                
                # Print summary
                print("\n===== SCRAPING SUMMARY =====", flush=True)
                print(f"Total pages processed: {len(results)}", flush=True)
                print(f"Total articles extracted: {sum(r['count'] for r in results)}", flush=True)
                print("============================", flush=True)
                
            finally:
                # Always close the driver
                driver.quit()
                print("WebDriver closed", flush=True)
        
        # Multi-threaded mode
        else:
            print(f"Running in multi-threaded mode with {max_workers} workers", flush=True)
            
            # Divide pages among workers
            page_assignments = divide_pages(start_page, end_page, max_workers)
            actual_workers = len(page_assignments)
            
            print(f"Page assignments: {page_assignments}", flush=True)
            print(f"Using {actual_workers} workers", flush=True)
            
            all_results = []
            
            # Create thread pool
            with ThreadPoolExecutor(max_workers=actual_workers) as executor:
                # Submit worker tasks
                future_to_worker = {
                    executor.submit(worker_process, i+1, pages, conn, verbose): i+1 
                    for i, pages in enumerate(page_assignments)
                }
                
                # Process results
                for future in future_to_worker:
                    worker_id = future_to_worker[future]
                    try:
                        worker_results = future.result()
                        all_results.extend(worker_results)
                        worker_total = sum(r['count'] for r in worker_results)
                        print(f"Worker {worker_id} completed with {worker_total} total articles", flush=True)
                    except Exception as e:
                        print(f"Worker {worker_id} failed: {str(e)}", flush=True)
            
            # Print summary
            successful = sum(1 for r in all_results if r['status'] == 'success')
            no_results = sum(1 for r in all_results if r['status'] == 'no_results')
            total_articles = sum(r['count'] for r in all_results)
            
            print("\n===== SCRAPING SUMMARY =====", flush=True)
            print(f"Total pages processed: {len(all_results)}", flush=True)
            print(f"Pages with results: {successful}", flush=True)
            print(f"Pages without results: {no_results}", flush=True)
            print(f"Total articles extracted: {total_articles}", flush=True)
            print("============================", flush=True)
    
    finally:
        conn.close()
        print("Database connection closed", flush=True)

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