#!/usr/bin/env python3
"""
Command-line interface for the McKinsey search scraper.
"""

import argparse
import logging
import sys
import json
from mckinsey_scraper import scrape_mckinsey_search
from database_utils import export_to_csv, export_content_to_csv, get_database_stats, get_session, Article, ArticleContent, get_article_count, get_article_content_count
from article_scraper import scrape_all_unscrapped_articles

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
    scrape_parser.add_argument('-q', '--query', required=True, help='Search query')
    scrape_parser.add_argument('--full', action='store_true', help='Scrape all pages (not just the first)')
    scrape_parser.add_argument('--pages', type=int, default=5, help='Maximum number of pages to scrape (default: 5)')
    
    # Scrape content command
    content_parser = subparsers.add_parser('scrape-content', help='Scrape content of individual articles')
    content_parser.add_argument('-l', '--limit', type=int, default=5,
                              help='Maximum number of articles to scrape (default: 5, 0 for all)')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    
    # List articles command
    list_parser = subparsers.add_parser('list', help='List articles in the database')
    list_parser.add_argument('-l', '--limit', type=int, default=10,
                           help='Maximum number of articles to list')
    list_parser.add_argument('-o', '--offset', type=int, default=0,
                           help='Offset for pagination')
    
    # List content command
    list_content_parser = subparsers.add_parser('list-content', help='List article contents in the database')
    list_content_parser.add_argument('-l', '--limit', type=int, default=5,
                                   help='Maximum number of article contents to list')
    list_content_parser.add_argument('-o', '--offset', type=int, default=0,
                                   help='Offset for pagination')
    
    # Export articles command
    export_parser = subparsers.add_parser('export', help='Export articles to CSV')
    export_parser.add_argument('-f', '--filename', type=str, default='mckinsey_articles.csv',
                             help='Output CSV filename')
    
    # Export content command
    export_content_parser = subparsers.add_parser('export-content', help='Export article contents to CSV')
    export_content_parser.add_argument('-f', '--filename', type=str, default='mckinsey_articles_content.csv',
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
        test_mode = not args.full
        article_count = scrape_mckinsey_search(args.query, test_mode=test_mode, max_pages=args.pages)
        logger.info(f"Scraping completed. Stored {article_count} articles.")
    
    elif args.command == 'scrape-content':
        limit = args.limit
        if limit == 0:
            logger.info("Scraping content for all unprocessed articles")
        else:
            logger.info(f"Scraping content for up to {limit} unprocessed articles")
        
        article_count = scrape_all_unscrapped_articles(limit=limit if limit > 0 else None)
        logger.info(f"Content scraping completed. Scraped {article_count} articles.")
    
    elif args.command == 'stats':
        stats = get_database_stats()
        logger.info(f"Database Statistics:")
        logger.info(f"- Total Articles: {stats['total_articles']}")
        logger.info(f"- Articles with Content: {stats['articles_with_content']}")
        logger.info(f"- Articles without Content: {stats['articles_without_content']}")
    
    elif args.command == 'list':
        with get_session() as session:
            articles = session.query(Article).order_by(Article.scraped_at.desc()).offset(args.offset).limit(args.limit).all()
            
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
    
    elif args.command == 'list-content':
        with get_session() as session:
            contents = session.query(ArticleContent).order_by(ArticleContent.scraped_at.desc()).offset(args.offset).limit(args.limit).all()
            
            if not contents:
                logger.info("No article contents found in the database")
            else:
                logger.info(f"Listing {len(contents)} article contents (offset: {args.offset}):")
                for i, content in enumerate(contents, 1):
                    logger.info(f"{i}. {content.title}")
                    logger.info(f"   Article ID: {content.article_id}")
                    logger.info(f"   URL: {content.url}")
                    if content.article_metadata:
                        try:
                            metadata = json.loads(content.article_metadata)
                            if 'authors' in metadata:
                                logger.info(f"   Authors: {', '.join(metadata['authors'])}")
                            if 'tags' in metadata:
                                logger.info(f"   Tags: {', '.join(metadata['tags'])}")
                        except:
                            pass
                    if content.full_content:
                        content_preview = content.full_content[:150].replace('\n', ' ')
                        logger.info(f"   Content preview: {content_preview}...")
                    logger.info("")
    
    elif args.command == 'export':
        success = export_to_csv(args.filename)
        if success:
            logger.info(f"Successfully exported articles to {args.filename}")
        else:
            logger.error(f"Failed to export articles to {args.filename}")
            sys.exit(1)
    
    elif args.command == 'export-content':
        success = export_content_to_csv(args.filename)
        if success:
            logger.info(f"Successfully exported article contents to {args.filename}")
        else:
            logger.error(f"Failed to export article contents to {args.filename}")
            sys.exit(1)


if __name__ == "__main__":
    main() 