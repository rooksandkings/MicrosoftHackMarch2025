# McKinsey Search Scraper

A Python web scraper for extracting articles from McKinsey's search results and storing them in a SQL database.

## Features

- Scrapes search results from McKinsey's website using the search query "change management"
- Uses Selenium WebDriver to render JavaScript content for reliable scraping
- Extracts article details including title, URL, description, publication date, and article type
- Can scrape the full content of individual articles including metadata
- Stores data in SQLite databases using SQLAlchemy ORM
- Provides a command-line interface for easy interaction
- Includes test mode for initial deployment (first page only)
- Handles pagination for scraping all available search result pages
- Includes error handling, retry logic, and rate limiting
- Exports data to CSV format

## Prerequisites

- Python 3.8 or higher
- Chrome or Chromium browser (for Selenium WebDriver)
- Required Python packages (see `requirements.txt`)
- Alternatively, Anaconda or Miniconda for conda environment setup

## Installation

### Using pip

1. Clone the repository or download the source code
2. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Using conda

1. Clone the repository or download the source code
2. Create and activate the conda environment:

```bash
conda env create -f environment.yml
conda activate mckinsey-scraper
```

## Usage

### Running the search results scraper

To run the scraper in test mode (first page only):

```bash
python cli.py scrape
```

To scrape all available pages:

```bash
python cli.py scrape --all-pages
```

To use a different search query:

```bash
python cli.py scrape --query "digital transformation"
```

### Scraping article content

After scraping search results, you can extract the full content of each article:

```bash
python cli.py scrape-content
```

By default, this will scrape up to 5 articles. To scrape more:

```bash
python cli.py scrape-content --limit 10
```

To scrape all available articles:

```bash
python cli.py scrape-content --limit 0
```

### Viewing statistics

To see statistics for both databases:

```bash
python cli.py stats
```

### Listing articles

To list the 10 most recently scraped articles:

```bash
python cli.py list
```

To specify a limit and offset:

```bash
python cli.py list --limit 20 --offset 10
```

### Listing article content

To list the 5 most recently scraped article contents:

```bash
python cli.py list-content
```

To specify a limit and offset:

```bash
python cli.py list-content --limit 10 --offset 5
```

### Exporting data

To export search results to a CSV file:

```bash
python cli.py export
```

To export article content to a CSV file:

```bash
python cli.py export-content
```

To specify a different output filename:

```bash
python cli.py export --filename custom_filename.csv
python cli.py export-content --filename content_export.csv
```

## Project Structure

- `mckinsey_scraper.py` - Main scraper implementation with Selenium WebDriver
- `article_scraper.py` - Module for scraping individual article content
- `database_utils.py` - Database utility functions
- `cli.py` - Command-line interface
- `requirements.txt` - Project dependencies
- `environment.yml` - Conda environment specification
- `README.md` - Project documentation

## Database Schema

### Search Results Database (mckinsey_articles.db)

| Column         | Type      | Description                       |
|----------------|-----------|-----------------------------------|
| id             | Integer   | Primary key                       |
| title          | String    | Article title                     |
| url            | String    | Article URL (unique)              |
| description    | Text      | Article description               |
| date_published | String    | Publication date                  |
| article_type   | String    | Type of article                   |
| scraped_at     | DateTime  | When the article was scraped      |

### Article Content Database (mckinsey_articles_content.db)

| Column           | Type      | Description                       |
|------------------|-----------|-----------------------------------|
| id               | Integer   | Primary key                       |
| article_id       | Integer   | Foreign key to articles table     |
| title            | String    | Article title                     |
| url              | String    | Article URL (unique)              |
| full_content     | Text      | Full article text content         |
| html_content     | Text      | HTML content of the article       |
| article_metadata | Text      | JSON string with article metadata |
| scraped_at       | DateTime  | When the content was scraped      |

## Recent Updates

- **Content Formatting Fix**: Fixed an issue where publication date and author bylines were improperly formatted in article content. The scraper now correctly adds proper spacing between the year and "by" text in author attributions (e.g., "2024 by" is now correctly formatted as "2024 by").

## Troubleshooting

### Chrome WebDriver Issues

1. **Driver Not Found**: If you get an error about the Chrome driver not being found:

   ```
   webdriver_manager.core.driver_cache.DriverCacheError: There is no such driver by url https://chromedriver.storage.googleapis.com/LATEST_RELEASE_
   ```

   Install Chrome browser or update to a supported version:
   
   ```bash
   # On Ubuntu/Debian
   sudo apt update
   sudo apt install chromium-browser
   
   # On Windows
   # Download the latest Chrome from https://www.google.com/chrome/
   ```

2. **Headless Mode Issues**: If the scraper can't render pages properly in headless mode, try disabling it by modifying the `create_webdriver()` function in `mckinsey_scraper.py`:

   ```python
   # Change this line:
   options.add_argument("--headless")
   
   # To:
   # options.add_argument("--headless")  # Commented out to disable headless mode
   ```

3. **Permission Issues**: If you encounter permission issues with ChromeDriver:
   
   ```bash
   # On Linux/Mac
   chmod +x /path/to/chromedriver
   ```

### CSS Selector Issues

If the scraper isn't finding any results, the CSS selectors might need adjustment. Try:

1. Run in non-headless mode to see the page structure
2. Inspect the page manually to identify correct selectors
3. Update the selectors in `parse_articles()` function

### Rate Limiting

If you're getting blocked by McKinsey's website:

1. Increase the delay between requests:
   
   ```python
   # In mckinsey_scraper.py, find:
   time.sleep(random.uniform(3, 7))
   
   # Change to:
   time.sleep(random.uniform(5, 10))
   ```

2. Use a proxy or VPN service
3. Reduce the number of pages scraped at once

### Content Formatting Issues

If you notice issues with content formatting in the exported CSV:

1. Check the exported CSV for proper spacing between dates and author bylines
2. The scraper includes regex to fix common formatting issues like missing spaces between year and "by" text
3. If new formatting issues arise, they can be addressed in the `extract_article_content()` function in `article_scraper.py`

## License

MIT License

## Disclaimer

This scraper is for educational purposes only. Please respect McKinsey's terms of service and robots.txt when using this tool. Implement appropriate delays between requests to avoid overloading their servers.