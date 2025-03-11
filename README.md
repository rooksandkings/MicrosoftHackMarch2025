# McKinsey Search Scraper

A Python web scraper for extracting articles from McKinsey's search results and storing them in a SQL database.

## Features

- Scrapes search results from McKinsey's website using the search query "change management"
- Extracts article details including title, URL, description, publication date, and article type
- Stores data in a SQLite database using SQLAlchemy ORM
- Provides a command-line interface for easy interaction
- Includes test mode for initial deployment (first page only)
- Handles pagination for scraping all available search result pages
- Includes error handling, retry logic, and rate limiting
- Exports data to CSV format

## Prerequisites

- Python 3.8 or higher
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

### Running the scraper

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

### Viewing statistics

To see how many articles are in the database:

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

### Exporting to CSV

To export all articles to a CSV file:

```bash
python cli.py export
```

To specify a different output filename:

```bash
python cli.py export --filename output.csv
```

## Project Structure

- `mckinsey_scraper.py` - Main scraper implementation
- `database_utils.py` - Database utility functions
- `cli.py` - Command-line interface
- `requirements.txt` - Project dependencies
- `environment.yml` - Conda environment specification
- `README.md` - Project documentation

## Database Schema

The scraper stores articles in a SQLite database with the following schema:

| Column         | Type      | Description                       |
|----------------|-----------|-----------------------------------|
| id             | Integer   | Primary key                       |
| title          | String    | Article title                     |
| url            | String    | Article URL (unique)              |
| description    | Text      | Article description               |
| date_published | String    | Publication date                  |
| article_type   | String    | Type of article                   |
| scraped_at     | DateTime  | When the article was scraped      |

## License

MIT License

## Disclaimer

This scraper is for educational purposes only. Please respect McKinsey's terms of service and robots.txt when using this tool. Implement appropriate delays between requests to avoid overloading their servers.