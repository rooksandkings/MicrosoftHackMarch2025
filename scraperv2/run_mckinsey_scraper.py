#!/usr/bin/env python3
import argparse
import sys
from mckinsey_scraper import main

def parse_args():
    parser = argparse.ArgumentParser(description='Scrape McKinsey articles about change management')
    
    parser.add_argument('-s', '--start-page', 
                        type=int, 
                        default=1,
                        help='First page to scrape (default: 1)')
    
    parser.add_argument('-e', '--end-page', 
                        type=int, 
                        default=5,
                        help='Last page to scrape (default: 5)')
    
    parser.add_argument('-w', '--workers', 
                        type=int, 
                        default=3,
                        help='Number of parallel workers (default: 3)')
    
    parser.add_argument('-v', '--verbose', 
                        action='store_true',
                        help='Enable verbose output')
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    if args.verbose:
        print(f"Starting McKinsey scraper with settings:")
        print(f"  Start page: {args.start_page}")
        print(f"  End page: {args.end_page}")
        print(f"  Workers: {args.workers}")
    
    try:
        main(start_page=args.start_page, 
             end_page=args.end_page, 
             max_workers=args.workers)
        
        print("Scraping completed successfully!")
        
    except Exception as e:
        print(f"Error during scraping: {e}", file=sys.stderr)
        sys.exit(1) 