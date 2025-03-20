"""
McKinsey link extraction utilities.
Contains functions for extracting article links and metadata.
"""

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re

def extract_article_links(driver, page_number):
    """Extract article links from McKinsey search page."""
    print("Extracting article links...", flush=True)
    links_data = []
    
    try:
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/our-insights/'], a[href*='/featured-insights/']")
        
        if not links:
            print("[!] No suitable links found", flush=True)
            return []
            
        print(f"[OK] Found {len(links)} potential article links", flush=True)
        
        for idx, link in enumerate(links[:10], 1):
            try:
                title = link.text.strip()
                url = link.get_attribute("href")
                
                # Skip empty or navigational links
                if len(title) < 5 or "next page" in title.lower() or "previous" in title.lower():
                    continue
                    
                print(f"  [OK] Found article link: {title}", flush=True)
                
                # Extract metadata from parent container
                try:
                    parent = link
                    for _ in range(5):  # Try going up a few levels
                        parent = parent.find_element(By.XPATH, '..')
                        parent_text = parent.text
                        if len(parent_text) > 100:  # Found a substantial container
                            break
                    
                    # Extract metadata using pattern matching
                    authors = extract_authors_from_text(parent_text)
                    date = extract_date_from_text(parent_text)
                    
                    links_data.append({
                        "title": title,
                        "url": url,
                        "page_number": page_number,
                        "authors": authors,
                        "date": date
                    })
                except Exception as e:
                    links_data.append({
                        "title": title,
                        "url": url,
                        "page_number": page_number,
                        "authors": "Not specified",
                        "date": "Not specified"
                    })
                    
            except Exception as e:
                print(f"  [!] Error processing link: {str(e)}", flush=True)
        
        print(f"[OK] Extracted {len(links_data)} article links", flush=True)
        return links_data
            
    except Exception as e:
        print(f"[!] Error during link extraction: {str(e)}", flush=True)
        return []

def extract_authors_from_text(text):
    """Extract authors from text content using pattern matching."""
    # Look for author pattern: Starts with "By " and continues until a new line
    author_match = re.search(r'By\s+([^\.]+?)\n', text)
    if author_match:
        return author_match.group(1).strip()
    
    # Try alternative patterns
    author_lines = [line for line in text.split('\n') if line.strip().startswith('By ')]
    if author_lines:
        return author_lines[0].replace('By ', '').strip()
    
    return "Not specified"

def extract_date_from_text(text):
    """Extract date from text content using pattern matching."""
    # Format: Category | Type | Date
    date_pattern = re.search(r'\|\s*(\w+\s+\d{1,2},\s*\d{4})', text)
    if date_pattern:
        return date_pattern.group(1).strip()
    
    # Alternative: Look for month names followed by dates
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 
              'August', 'September', 'October', 'November', 'December']
    
    for month in months:
        month_pattern = re.search(r'(' + month + r'\s+\d{1,2},\s*\d{4})', text)
        if month_pattern:
            return month_pattern.group(1).strip()
    
    return "Not specified"

def extract_authors(article_element):
    """Extract authors from an article element."""
    # Try text pattern matching first
    try:
        article_text = article_element.text
        authors = extract_authors_from_text(article_text)
        if authors != "Not specified":
            return authors
    except:
        pass
    
    # Try with selectors as fallback
    selectors = [".author", ".byline", ".authors", "[data-test='author']"]
    for selector in selectors:
        try:
            element = article_element.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except NoSuchElementException:
            continue
    
    return "Not specified"

def extract_date(article_element):
    """Extract publication date from an article element."""
    # Try text pattern matching first
    try:
        article_text = article_element.text
        date = extract_date_from_text(article_text)
        if date != "Not specified":
            return date
    except:
        pass
    
    # Try with selectors as fallback
    selectors = [".date", ".published-date", "[data-test='date']"]
    for selector in selectors:
        try:
            element = article_element.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except NoSuchElementException:
            continue
    
    return "Not specified"

def analyze_page_structure(driver):
    """Analyze page structure for debugging extraction issues."""
    try:
        page_text = driver.find_element(By.TAG_NAME, "body").text
        lines = page_text.split('\n')
        
        # Basic analysis of content patterns
        author_count = len([line for line in lines if line.strip().startswith('By ')])
        date_count = len([line for line in lines if '|' in line])
        
        print(f"[DEBUG] Found {author_count} author lines and {date_count} potential date lines", flush=True)
    except Exception as e:
        print(f"[DEBUG] Analysis error: {str(e)}", flush=True)
    
    return {"analysis_completed": True} 