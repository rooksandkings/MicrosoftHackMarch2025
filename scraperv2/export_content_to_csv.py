"""
Utility script to export the McKinsey content database to CSV.
"""

import sqlite3
import csv
import argparse
import sys
import os
import html
import re
import unicodedata

def connect_to_database(db_path):
    """Connect to the SQLite database."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database {db_path} not found")
    
    conn = sqlite3.connect(db_path)
    conn.text_factory = str  # Use Python's default string handling
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def normalize_text(text):
    """
    Normalize and clean text content for CSV export
    """
    if not isinstance(text, str):
        return "" if text is None else str(text)
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Normalize Unicode (NFKC: compatibility decomposition, followed by canonical composition)
    text = unicodedata.normalize('NFKC', text)
    
    # Replace common problematic characters
    replacements = {
        '\u2018': "'", # Left single quote
        '\u2019': "'", # Right single quote
        '\u201c': '"', # Left double quote
        '\u201d': '"', # Right double quote
        '\u2013': '-', # En dash
        '\u2014': '--', # Em dash
        '\u2026': '...', # Ellipsis
        '\u00A0': ' ', # Non-breaking space
        # Add more replacements as needed
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
        
    # Remove control characters except for tabs and newlines
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    return text

def export_to_csv(db_path, csv_path, include_content=True, include_all_columns=False, excel_compatible=True):
    """Export database content to CSV file with proper encoding throughout."""
    print(f"Exporting from {db_path} to {csv_path}")
    
    # Connect to database with explicit UTF-8 handling
    conn = sqlite3.connect(db_path)
    conn.text_factory = str  # Use Python's default string handling
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Determine table name by checking what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if 'article_content' in tables:
            table_name = 'article_content'
        elif 'articles' in tables:
            table_name = 'articles'
        else:
            raise ValueError(f"No article tables found in database. Available tables: {tables}")
        
        print(f"Using table: {table_name}")
        
        # Get all column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        all_columns = [column[1] for column in cursor.fetchall()]
        
        # Define columns to exclude by default
        excluded_columns = []  # Keep all columns in the new structure
        
        # Define columns to include
        if include_all_columns:
            columns = all_columns
        else:
            columns = [col for col in all_columns if col not in excluded_columns]
            
        # If not including content, remove it from columns
        if not include_content and 'content' in columns:
            columns = [col for col in columns if col != 'content']
        
        # Get all data
        cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            print("No data found in the database.")
            return
        
        print(f"Found {len(rows)} articles to export")
        
        # Excel character limit per cell
        EXCEL_CELL_LIMIT = 32000  # Using 32000 to be safe (actual limit is 32,767)
        
        # Write to CSV with explicit UTF-8 encoding
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csv_file:  # UTF-8 with BOM for Excel
            writer = csv.writer(csv_file, 
                               quoting=csv.QUOTE_ALL,
                               quotechar='"',
                               escapechar='\\',
                               doublequote=True)
            
            # Write header
            writer.writerow(columns)
            
            # Write data rows
            for row in rows:
                # Convert row to dictionary for easier column access
                row_dict = dict(row)
                
                # Create a properly sanitized row
                sanitized_row = []
                for col in columns:
                    value = row_dict.get(col, '')
                    if value is None:
                        sanitized_row.append('')
                    else:
                        # Convert to string if it's not already
                        value = str(value)
                        
                        # Normalize text to handle special characters
                        value = normalize_text(value)
                        
                        # Truncate content if it's too long for Excel
                        if excel_compatible and col == 'content' and len(value) > EXCEL_CELL_LIMIT:
                            value = value[:EXCEL_CELL_LIMIT] + " [truncated for Excel compatibility]"
                        
                        sanitized_row.append(value)
                
                writer.writerow(sanitized_row)
        
        print(f"Successfully exported {len(rows)} articles to {csv_path}")
        
        if excel_compatible:
            print(f"Note: Content fields longer than {EXCEL_CELL_LIMIT} characters were truncated for Excel compatibility.")
            print(f"To export full content without truncation, run with --no-excel-limit flag.")
        
    except Exception as e:
        print(f"Error exporting to CSV: {str(e)}")
        raise
        
    finally:
        conn.close()

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description='Export McKinsey content database to CSV.')
    parser.add_argument('-d', '--database', default='mckinsey_article_content.db',
                        help='Path to the content database (default: mckinsey_article_content.db)')
    parser.add_argument('-o', '--output', default='mckinsey_articles_export.csv',
                        help='Path to the output CSV file (default: mckinsey_articles_export.csv)')
    parser.add_argument('--no-content', action='store_true',
                        help='Exclude article content from CSV export')
    parser.add_argument('--all-columns', action='store_true',
                        help='Include all columns including redundant ones')
    parser.add_argument('--no-excel-limit', action='store_true',
                        help='Export full content without Excel cell size limits')
    
    args = parser.parse_args()
    
    try:
        export_to_csv(args.database, args.output, 
                      not args.no_content, 
                      args.all_columns, 
                      not args.no_excel_limit)
        print("Export completed successfully!")
    except Exception as e:
        print(f"Error during export: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 