#!/usr/bin/env python3
"""
Command-line interface for the McKinsey search scraper.
"""

import argparse
import logging
import sys
from mckinsey_scraper import scrape_mckinsey_search
from database_utils import get_article_count, get_articles, export_to_csv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='McKinsey Search Scraper CLI')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape McKinsey search results')
    scrape_parser.add_argument('-q', '--query', type=str, default='change management',
                             help='Search query (default: "change management")')
    scrape_parser.add_argument('-a', '--all-pages', action='store_true',
                             help='Scrape all pages, not just the first one')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List articles in the database')
    list_parser.add_argument('-l', '--limit', type=int, default=10,
                           help='Maximum number of articles to list')
    list_parser.add_argument('-o', '--offset', type=int, default=0,
                           help='Offset for pagination')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export articles to CSV')
    export_parser.add_argument('-f', '--filename', type=str, default='mckinsey_articles.csv',
                             help='Output CSV filename')
    
    return parser.parse_args()


def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    if not args.command:
        logger.error("No command specified. Use -h for help.")
        sys.exit(1)
    
    # Execute command
    if args.command == 'scrape':
        logger.info(f"Scraping McKinsey search results for query: {args.query}")
        test_mode = not args.all_pages
        if test_mode:
            logger.info("Test mode: Only scraping the first page")
        else:
            logger.info("Full mode: Scraping all pages")
        
        article_count = scrape_mckinsey_search(args.query, test_mode=test_mode)
        logger.info(f"Scraping completed. Stored {article_count} articles.")
    
    elif args.command == 'stats':
        count = get_article_count()
        logger.info(f"Total articles in database: {count}")
    
    elif args.command == 'list':
        articles = get_articles(limit=args.limit, offset=args.offset)
        if not articles:
            logger.info("No articles found in the database")
        else:
            logger.info(f"Listing {len(articles)} articles (offset: {args.offset}):")
            for i, article in enumerate(articles, 1):
                logger.info(f"{i}. {article.title} ({article.date_published})")
                logger.info(f"   URL: {article.url}")
                if article.description:
                    logger.info(f"   Description: {article.description[:100]}...")
                logger.info("")
    
    elif args.command == 'export':
        success = export_to_csv(args.filename)
        if success:
            logger.info(f"Successfully exported articles to {args.filename}")
        else:
            logger.error(f"Failed to export articles to {args.filename}")
            sys.exit(1)


if __name__ == "__main__":
    main() 