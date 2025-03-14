#!/usr/bin/env python3
"""
Command-line interface for the McKinsey search scraper.
"""

import mckinsey_scraper
import logging
import argparse
import sys
from datetime import datetime
import time
from database_utils import export_to_csv, export_content_to_csv
from article_scraper import scrape_article_content, scrape_multiple_articles
from mckinsey_scraper import create_webdriver  # Assuming this function exists
import csv
from mckinsey_scraper import get_session, Article

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def create_parser():
    parser = argparse.ArgumentParser(description='McKinsey Article Scraper')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape McKinsey search results')
    scrape_parser.add_argument('-q', '--query', required=True, help='Search query')
    scrape_parser.add_argument('--full', action='store_true', help='Scrape all pages (not just the first)')
    scrape_parser.add_argument('--pages', type=int, default=5, help='Maximum number of pages to scrape (default: 5)')
    scrape_parser.add_argument('--parallel', action='store_true', help='Use parallel scraping')
    scrape_parser.add_argument('--workers', type=int, default=3, help='Number of parallel workers (default: 3)')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process articles')
    process_parser.add_argument('--count', type=int, default=10, help='Number of articles to process')
    
    # Add export command
    export_parser = subparsers.add_parser('export', help='Export search results to CSV')
    export_parser.add_argument('--filename', default='mckinsey_articles.csv',
                              help='Output CSV filename (default: mckinsey_articles.csv)')
    
    # Add export-content command
    export_content_parser = subparsers.add_parser('export-content', help='Export article content to CSV')
    export_content_parser.add_argument('--filename', default='articles_content.csv',
                                      help='Output CSV filename (default: articles_content.csv)')
    
    # Add scrape-content command
    scrape_content_parser = subparsers.add_parser('scrape-content', 
                                               help='Scrape full content of articles')
    scrape_content_parser.add_argument('--limit', type=int, default=5,
                                    help='Maximum number of articles to scrape (0 for unlimited)')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export articles to CSV')
    export_parser.add_argument('--output', '-o', default='mckinsey_articles.csv', 
                              help='Output CSV file path (default: mckinsey_articles.csv)')
    export_parser.add_argument('--limit', type=int, default=0, 
                              help='Limit number of articles to export (0 for all)')
    
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
        
    elif args.command == 'scrape':
        test_mode = not args.full
        
        # Start timing the operation
        start_time = time.time()
        
        # Use parallel scraping
        logger.info(f"Starting scraping for query: {args.query}")
        article_count = mckinsey_scraper.scrape_mckinsey_search_parallel(
            args.query, 
            test_mode=test_mode, 
            max_pages=args.pages,
            max_workers=args.workers
        )
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        logger.info(f"Scraping completed in {elapsed_time:.2f} seconds. Stored {article_count} articles.")
        
    elif args.command == 'process':
        # This will need to be implemented with appropriate module functions
        logger.info(f"Processing up to {args.count} articles")
        # Process articles code here
        
    elif args.command == 'export':
        logger.info(f"Exporting articles to CSV: {args.output}")
        
        # Get articles from database
        with get_session() as session:
            query = session.query(Article)
            
            if args.limit > 0:
                query = query.limit(args.limit)
                
            articles = query.all()
        
        # Write to CSV
        with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'title', 'url', 'description', 'date_published', 
                         'article_type', 'content', 'scraped_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for article in articles:
                writer.writerow({
                    'id': article.id,
                    'title': article.title,
                    'url': article.url,
                    'description': article.description,
                    'date_published': article.date_published,
                    'article_type': article.article_type,
                    'content': article.content,
                    'scraped_at': article.scraped_at
                })
        
        logger.info(f"Exported {len(articles)} articles to {args.output}")
    
    elif args.command == 'export-content':
        logger.info(f"Exporting article content to CSV: {args.filename}")
        try:
            from database_utils import export_content_to_csv
            result = export_content_to_csv(args.filename)
            
            # Check if result is boolean or numeric
            if isinstance(result, bool):
                if result:
                    logger.info(f"Successfully exported articles to {args.filename}")
                else:
                    logger.warning(f"No articles were exported to {args.filename}")
            else:
                # Result is a count
                logger.info(f"Successfully exported {result} articles to {args.filename}")
        except Exception as e:
            logger.error(f"Error exporting content to CSV: {e}")
    
    elif args.command == 'scrape-content':
        logger.info(f"Scraping content for up to {args.limit} articles")
        driver = None
        try:
            # Create a WebDriver instance
            logger.info("Creating WebDriver for article content scraping")
            driver = create_webdriver()
            if not driver:
                logger.error("Failed to create WebDriver")
                return
            
            # Scrape article content
            limit = args.limit if args.limit > 0 else None
            
            # Use the multiple article scraper instead of the single article one
            count = scrape_multiple_articles(driver, limit)
            
            logger.info(f"Successfully scraped content for {count} articles")
        except Exception as e:
            logger.error(f"Error scraping article content: {e}")
        finally:
            # Clean up resources
            if driver:
                try:
                    driver.quit()
                    logger.info("WebDriver closed")
                except Exception as e:
                    logger.warning(f"Error closing WebDriver: {e}")

if __name__ == '__main__':
    main() 