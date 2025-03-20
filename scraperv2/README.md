# McKinsey Article Scraper v2

A comprehensive toolset for scraping, parsing, and exporting McKinsey article content. This suite of tools allows you to collect and store article metadata, extract full article text, and export the content to CSV for analysis.

## Overview

This project consists of several integrated components:

- **mckinsey_scraper.py**: Collects article metadata from search results
- **article_parser.py**: Extracts full content from previously scraped article URLs
- **export_content_to_csv.py**: Exports the collected content to CSV format
- **Supporting modules**:
  - **cookie_handler.py**: Manages cookie consent popups
  - **link_extractor.py**: Extracts article links and metadata
  - **run_mckinsey_scraper.py**: Convenient wrapper with default parameters

## Requirements

- Python 3.6+
- Chrome/Chromium browser
- ChromeDriver (matching your Chrome version)
- Required Python packages (see Installation section)

## Installation

### Option 1: Using conda (recommended)

If you have Anaconda or Miniconda installed, you can create a new environment with all dependencies using the provided environment.yml file:

```
conda env create -f environment.yml
conda activate mckinsey-scraper
```

### Option 2: Manual installation

1. Clone this repository
2. Install required packages:
   ```
   pip install selenium requests beautifulsoup4 SQLAlchemy python-dotenv lxml fake-useragent webdriver-manager
   ```
3. Download ChromeDriver that matches your Chrome version from [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)
4. Ensure ChromeDriver is in your system PATH

## Usage

### Step 1: Scrape Article Metadata

First, collect article metadata from McKinsey search results:

```
python run_mckinsey_scraper.py --start-page 1 --end-page 5 --workers 3
```

Or use the base script with more options:

```
python mckinsey_scraper.py --start-page 1 --end-page 5 --workers 3 --verbose
```

Parameters:
- `--start-page` / `-s`: First page to scrape (default: 1)
- `--end-page` / `-e`: Last page to scrape (default: 5)
- `--workers` / `-w`: Number of parallel workers (default: 3)
- `--verbose` / `-v`: Enable detailed output

Output: Creates `mckinsey_articles.db` with article metadata (titles, authors, dates, URLs)

### Step 2: Extract Article Content

Next, extract full content from the collected article URLs:

```
python article_parser.py --workers 4 --verbose
```

Parameters:
- `--limit` / `-l`: Maximum number of articles to process
- `--workers` / `-w`: Number of concurrent workers (default: 1)
- `--verbose` / `-v`: Enable detailed output

Output: Creates `mckinsey_article_content.db` with full article text

### Step 3: Export Content to CSV

Finally, export the content to CSV format for analysis:

```
python export_content_to_csv.py
```

Parameters:
- `--database` / `-d`: Path to content database (default: mckinsey_article_content.db)
- `--output` / `-o`: Path to output CSV file (default: mckinsey_articles_export.csv)
- `--no-content`: Exclude article content from CSV export
- `--all-columns`: Include all columns including redundant ones
- `--no-excel-limit`: Export full content without Excel cell size limits

Output: Creates a CSV file with normalized article content

## Database Structure

### mckinsey_articles.db
- Table: `articles`
  - `id`: Unique identifier (primary key)
  - `title`: Article title
  - `authors`: Article authors
  - `date`: Publication date
  - `url`: Article URL (unique)
  - `page_number`: Search results page number

### mckinsey_article_content.db
- Table: `article_content`
  - `article_id`: Foreign key to articles.id (primary key)
  - `title`: Article title (copy)
  - `authors`: Article authors (copy)
  - `date`: Publication date (copy)
  - `url`: Article URL (copy)
  - `page_number`: Search page number (copy)
  - `content`: Full article text content

## Parallel Processing

Both the scraper and parser support parallel processing with multiple workers:

- Each worker maintains its own WebDriver instance
- Work is divided evenly among workers
- SQLite connections are thread-safe with `check_same_thread=False`
- Results are combined and saved centrally

Recommended worker counts:
- For scraping: 3-5 workers
- For parsing: 4-8 workers

## Notes

- The scraper respects website limitations by implementing random delays
- Cookie consent banners are automatically handled
- Duplicate entries are skipped using unique constraints
- Each run of the parser only processes previously unprocessed articles
- Content is normalized for CSV export with proper character handling
- Large content fields are truncated for Excel compatibility by default