"""
McKinsey Article Content Scraper

Extracts article content from McKinsey articles, focusing on the meaningful information
while preserving the document structure.
"""

import time
import random
import logging
import json
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import select
from database_utils import get_session, Article, ArticleContent
import re  # Add this to the imports at the top

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_unscrapped_articles(limit=None):
    """
    Get articles that haven't had their content scraped yet.
    """
    try:
        with get_session() as session:
            # Get articles that need content scraping
            subquery = select(ArticleContent.article_id)
            query = session.query(Article).filter(
                ~Article.id.in_(subquery)
            )
            
            if limit:
                query = query.limit(limit)
            
            # Create a list of article data instead of returning ORM objects
            articles_data = [
                {
                    'id': article.id,
                    'title': article.title,
                    'url': article.url
                }
                for article in query.all()
            ]
            
            logger.info(f"Found {len(articles_data)} articles that need content scraping")
            return articles_data
            
    except Exception as e:
        logger.error(f"Error getting unscrapped articles: {e}")
        return []

def handle_cookie_consent(driver):
    """
    Handle cookie consent on McKinsey website.
    """
    try:
        # McKinsey uses OneTrust for cookie consent
        cookie_selectors = [
            "button#onetrust-accept-btn-handler",
            "button.consent-accept",
            "#onetrust-consent-sdk button[aria-label='Accept all cookies']"
        ]
        
        for selector in cookie_selectors:
            try:
                cookie_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                logger.info(f"Found cookie consent button: {selector}")
                cookie_btn.click()
                time.sleep(2)
                logger.info("Cookie consent handled successfully")
                return True
            except:
                continue
                
        return False
    except Exception as e:
        logger.warning(f"Error handling cookie consent: {e}")
        return False

def scrape_multiple_articles(driver, limit=None):
    """
    Scrape content for multiple articles up to the specified limit.
    
    Args:
        driver: Selenium WebDriver instance
        limit (int, optional): Maximum number of articles to scrape, None for all
        
    Returns:
        int: Number of articles successfully scraped
    """
    try:
        # Get unscrapped articles
        unscrapped_articles = get_unscrapped_articles(limit)
        
        if not unscrapped_articles:
            logger.info("No articles found that need content scraping")
            return 0
            
        logger.info(f"Found {len(unscrapped_articles)} articles to scrape")
        
        # Track success count
        success_count = 0
        
        # Process each article
        for i, article in enumerate(unscrapped_articles):
            logger.info(f"Processing article {i+1}/{len(unscrapped_articles)}: {article['title']}")
            
            # Add random delay between requests (1-3 seconds)
            if i > 0:
                delay = random.uniform(1, 3)
                logger.info(f"Waiting {delay:.1f} seconds before next article...")
                time.sleep(delay)
                
            # Scrape the article content
            success = scrape_article_content(driver, article)
            
            if success:
                success_count += 1
                
        logger.info(f"Successfully scraped content for {success_count} out of {len(unscrapped_articles)} articles")
        return success_count
        
    except Exception as e:
        logger.error(f"Error scraping multiple articles: {e}")
        return 0

def extract_article_metadata(soup):
    """
    Extract metadata like authors and publication date from McKinsey articles.
    Focus on reliable extraction patterns based on CSV analysis.
    """
    metadata = {}
    authors = []
    
    # Extract publication date - prioritize structured formats
    try:
        # First try meta tags which are most reliable
        meta_date = soup.find('meta', {'property': ['article:published_time', 'og:published_time', 'publication_date']})
        if meta_date and meta_date.get('content'):
            metadata['publication_date'] = meta_date.get('content')
        else:
            # Then try common date elements
            date_selectors = ['time', '.date', '.article-date', '.timestamp']
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    metadata['publication_date'] = date_elem.text.strip()
                    break
                    
            # If still not found, look for date patterns in first few paragraphs
            if 'publication_date' not in metadata:
                paragraphs = soup.find_all('p')[:5]
                for p in paragraphs:
                    text = p.text.strip()
                    date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}', text)
                    if date_match:
                        metadata['publication_date'] = date_match.group(0)
                        break
    except Exception as e:
        logger.warning(f"Error extracting publication date: {e}")
    
    # Extract authors - McKinsey specific patterns - FIX: Enhanced pattern matching
    try:
        # First try byline elements which are most reliable
        byline_selectors = ['.byline', '.author', '.article-author', '[itemprop="author"]', '.article-byline']
        for selector in byline_selectors:
            author_elements = soup.select(selector)
            if author_elements:
                for element in author_elements:
                    author_text = element.text.strip()
                    if author_text and len(author_text) < 100:
                        # Clean up "by" prefix if present
                        if author_text.lower().startswith('by '):
                            author_text = author_text[3:].strip()
                        authors.append(author_text)
                break
        
        # If no authors found via elements, try meta tags
        if not authors:
            meta_author = soup.find('meta', {'name': 'author'})
            if meta_author and meta_author.get('content'):
                authors.append(meta_author.get('content'))
        
        # If still no authors, try looking in text paragraphs
        if not authors:
            # Look for patterns in the first few paragraphs
            paragraphs = soup.find_all('p')[:5]
            
            for p in paragraphs:
                text = p.text.strip()
                
                # McKinsey often puts authors right after the publication date
                # Pattern: "Month Day, Year by Author1, Author2, and Author3"
                date_by_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\s*by\s+(.*?)(\.|$)', text, re.IGNORECASE)
                if date_by_match:
                    author_text = date_by_match.group(2).strip()
                    if author_text and len(author_text) < 200:
                        # Split multiple authors on commas or "and"
                        if ',' in author_text or ' and ' in author_text.lower():
                            author_list = re.split(r',\s*|\s+and\s+', author_text)
                            authors.extend([a.strip() for a in author_list if a.strip()])
                        else:
                            authors.append(author_text)
                    break
                
                # Also look for "by Author" or "by Author1, Author2" without date
                by_author_match = re.search(r'\bby\s+(.*?)(\.|$)', text, re.IGNORECASE)
                if by_author_match and not authors:
                    author_text = by_author_match.group(1).strip()
                    if author_text and len(author_text) < 100:
                        if ',' in author_text or ' and ' in author_text.lower():
                            author_list = re.split(r',\s*|\s+and\s+', author_text)
                            authors.extend([a.strip() for a in author_list if a.strip()])
                        else:
                            authors.append(author_text)
                    break
    except Exception as e:
        logger.warning(f"Error extracting authors: {e}")
    
    # Clean and deduplicate authors
    if authors:
        # Remove duplicates while preserving order
        seen = set()
        authors = [a for a in authors if not (a.lower() in seen or seen.add(a.lower()))]
        
        # Store authors in metadata
        metadata['authors'] = authors
        
    return metadata, authors

def extract_article_content(soup):
    """
    Extract article content with improved filtering to remove redundant and irrelevant content.
    """
    try:
        # Content container identification
        content_selectors = [
            "article",
            ".article-body",
            ".main-content", 
            "#article-content",
            ".content-wrapper",
            "main"
        ]
        
        content_container = None
        for selector in content_selectors:
            containers = soup.select(selector)
            if containers:
                content_container = max(containers, key=lambda x: len(x.get_text().strip()))
                break
        
        # Fallback to body if no container found
        if not content_container:
            content_container = soup.body
            
        # Remove unnecessary elements that appear in the content
        noise_selectors = [
            # Cookie-related elements
            '.cookie-banner', '#onetrust-banner-sdk', '.cookie-consent', '.gdpr',
            # Navigation elements
            'nav', '.navigation', '.menu', '.nav', '.navbar',
            # Footer elements
            'footer', '.footer',
            # Sidebar elements
            'aside', '.sidebar', '.widgets', '.related-content',
            # Ads and subscription elements
            '.ads', '.advertisement', '.subscribe', '.subscription', '.paywall',
            # Social media
            '.social-share', '.share-buttons', '.social-media',
            # Comments
            '.comments', '.comment-section',
            # Newsletter and CTA elements
            '.newsletter', '.signup', '.cta', '.call-to-action',
            # Copyright notices
            '.copyright', '.legal', '.terms',
            # Image captions that may be repetitive
            '.image-caption', '.figure-caption'
        ]
        
        for selector in noise_selectors:
            for element in content_container.select(selector):
                element.decompose()
        
        # Clean content text
        paragraphs = []
        for p in content_container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
            text = p.get_text().strip()
            
            # Skip empty paragraphs
            if not text:
                continue
                
            # Skip cookie notices and other common non-article text patterns
            if any(phrase in text.lower() for phrase in [
                'cookie', 'privacy policy', 'terms of use', 'accept all', 'we use cookies',
                'newsletter', 'subscribe', 'sign up', 'email address',
                'all rights reserved', '©', 'copyright',
                'never miss an insight', 'click', 'download'
            ]):
                continue
                
            # Skip short non-content paragraphs
            if len(text) < 20 and not p.name.startswith('h'):
                continue
                
            # Fix date formatting issues (add space between year and "by")
            text = re.sub(r'(\d{4})by\s+', r'\1 by ', text)
            
            # Add proper formatting based on element type
            if p.name.startswith('h'):
                paragraphs.append(f"\n## {text}\n")
            elif p.name == 'li':
                paragraphs.append(f"• {text}")
            else:
                paragraphs.append(text)
        
        # Join paragraphs with proper spacing
        content = "\n\n".join(paragraphs)
        
        # Remove excessive whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()
        
    except Exception as e:
        logger.error(f"Error extracting article content: {e}")
        return None

def store_article_content(article_id, title, url, full_content, metadata):
    """
    Store article content in the database, removing redundant information.
    """
    try:
        # Extract metadata and authors
        metadata_dict, authors_list = metadata
        
        # Convert authors list to string
        authors_str = ", ".join(authors_list) if authors_list else ""
        
        # Process content to remove redundancy
        if isinstance(full_content, str) and title in full_content:
            # Remove title from beginning of content if it's duplicated
            title_pattern = re.escape(title)
            full_content = re.sub(f"^{title_pattern}\s*", "", full_content)
        
        # Convert metadata to JSON, avoiding redundant storage
        clean_metadata = metadata_dict.copy()
        
        # Don't store publication date in metadata if it's just a duplicate of what's in the content
        if 'publication_date' in clean_metadata and clean_metadata['publication_date'] in full_content:
            del clean_metadata['publication_date']
            
        # Add article statistics
        word_count = len(full_content.split())
        clean_metadata['word_count'] = word_count
        clean_metadata['reading_time_minutes'] = max(1, round(word_count / 200))  # Assume 200 words per minute
        
        metadata_json = json.dumps(clean_metadata)
        
        with get_session() as session:
            # Check if article content already exists
            existing = session.query(ArticleContent).filter_by(article_id=article_id).first()
            if existing:
                logger.info(f"Article content already exists for article ID {article_id}")
                return False
                
            # Create new article content
            article_content = ArticleContent(
                article_id=article_id,
                title=title,
                url=url,
                full_content=full_content,
                authors=authors_str,  # Store authors as string
                article_metadata=metadata_json,
                processed=True,
                scraped_at=datetime.now()
            )
            session.add(article_content)
            session.commit()
            
            logger.info(f"Stored article content for article ID {article_id} with authors: {authors_str}")
            return True
            
    except Exception as e:
        logger.error(f"Error storing article content: {e}")
        return False

def scrape_article_content(driver, article):
    """
    Scrape article content with improved handling of input types.
    
    Args:
        driver: Selenium WebDriver instance
        article: Article object, dictionary, or ID
    """
    # Handle different input types
    if isinstance(article, int):
        # If article is just an ID, get the full article from database
        article_id = article
        with get_session() as session:
            article_obj = session.query(Article).filter_by(id=article_id).first()
            if not article_obj:
                logger.error(f"Article with ID {article_id} not found")
                return False
            title = article_obj.title
            url = article_obj.url
    elif isinstance(article, dict):
        # If article is a dictionary
        article_id = article.get('id')
        url = article.get('url')
        title = article.get('title')
    else:
        # If article is an object with attributes
        article_id = getattr(article, 'id', None)
        url = getattr(article, 'url', None)
        title = getattr(article, 'title', None)
    
    # Validate required fields
    if not article_id or not url:
        logger.error(f"Missing required article information: id={article_id}, url={url}")
        return False
        
    logger.info(f"Loading URL: {url}")
    
    try:
        # Navigate to article
        driver.get(url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Handle cookie consent if present
        try:
            # Check for common cookie consent buttons
            cookie_selectors = [
                'button#onetrust-accept-btn-handler',
                'button.accept-cookies',
                'button.consent-accept',
                'button.accept-all',
                'button[aria-label="Accept cookies"]',
                '.cookie-banner button[type="submit"]',
                '.cookie-consent button'
            ]
            
            for selector in cookie_selectors:
                cookie_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                if cookie_buttons:
                    logger.info(f"Found cookie consent button: {selector}")
                    try:
                        # Click the first visible button
                        for button in cookie_buttons:
                            if button.is_displayed():
                                button.click()
                                logger.info("Cookie consent handled successfully")
                                time.sleep(2)  # Wait for banner to disappear
                                break
                    except Exception as e:
                        logger.warning(f"Error clicking cookie consent button: {e}")
                    break
        except Exception as e:
            logger.warning(f"Error handling cookie consent: {e}")
        
        # Get page source after consent handling
        page_source = driver.page_source
        
        # Parse HTML
        soup = BeautifulSoup(page_source, 'lxml')
        
        # Extract content
        content = extract_article_content(soup)
        
        # Verify we got content
        if not content or len(content) < 100:
            logger.warning(f"Retrieved content is too short ({len(content) if content else 0} chars)")
            
            # Try alternative extraction method
            try:
                # Get all text from page body
                body = soup.body
                if body:
                    # Remove script and style elements
                    for script in body(["script", "style", "nav", "footer", "header"]):
                        script.decompose()
                    
                    # Get text and split into lines
                    lines = [line.strip() for line in body.get_text().split('\n') if line.strip()]
                    
                    # Filter out short lines and common non-content lines
                    filtered_lines = []
                    for line in lines:
                        # Skip short lines
                        if len(line) < 20:
                            continue
                            
                        # Skip lines with common non-content phrases
                        if any(phrase in line.lower() for phrase in [
                            'cookie', 'privacy policy', 'terms of use', 'accept all',
                            'all rights reserved', 'copyright', '©', 'subscription',
                            'sign up', 'newsletter', 'download'
                        ]):
                            continue
                            
                        filtered_lines.append(line)
                    
                    content = '\n\n'.join(filtered_lines)
                    logger.info(f"Extracted {len(content)} characters using fallback method")
            except Exception as e:
                logger.error(f"Error using fallback extraction: {e}")
        
        if content and len(content) > 0:
            logger.info(f"Extracted {len(content)} characters of content")
            
            # Extract metadata
            metadata = extract_article_metadata(soup)
            
            # Store content
            success = store_article_content(article_id, title, url, content, metadata)
            return success
        else:
            logger.error("Failed to extract content")
            return False
            
    except Exception as e:
        logger.error(f"Error scraping article content: {e}")
        return False

def export_content_to_csv(filename='articles_content.csv'):
    """
    Export all article contents to a CSV file.
    """
    try:
        from database_utils import export_content_to_csv as db_export
        return db_export(filename)
    except Exception as e:
        logger.error(f"Error exporting content to CSV: {e}")
        return False 