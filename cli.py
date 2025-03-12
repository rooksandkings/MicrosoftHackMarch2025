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
        
if __name__ == '__main__':
    main() 