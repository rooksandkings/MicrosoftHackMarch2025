import sqlite3
import csv
import os
import sys

def export_db_to_csv(db_file='mckinsey_articles.db', csv_file='links.csv'):
    """
    Export articles from SQLite database to CSV file
    
    Args:
        db_file (str): Path to SQLite database file
        csv_file (str): Path to output CSV file (default: links.csv)
    """
    print(f"Exporting database '{db_file}' to CSV file '{csv_file}'...")
    
    try:
        # Check if DB file exists
        if not os.path.exists(db_file):
            print(f"ERROR: Database file '{db_file}' not found")
            return False
            
        # Connect to database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get all articles
        cursor.execute("SELECT id, title, authors, date, url, page_number FROM articles ORDER BY id")
        rows = cursor.fetchall()
        
        if not rows:
            print("No articles found in database.")
            conn.close()
            return False
            
        # Write to CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # Write header
            csv_writer.writerow(['ID', 'Title', 'Authors', 'Date', 'URL', 'Page Number'])
            
            # Write data
            for row in rows:
                csv_writer.writerow(row)
        
        article_count = len(rows)
        print(f"Successfully exported {article_count} articles to '{csv_file}'")
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error exporting to CSV: {str(e)}")
        return False

if __name__ == "__main__":
    # Default file names
    db_file = 'mckinsey_articles.db'
    csv_file = 'mckinsey_articles_links.csv'
    
    # Allow custom file names from command line
    if len(sys.argv) > 1:
        db_file = sys.argv[1]
    if len(sys.argv) > 2:
        csv_file = sys.argv[2]
        
    export_db_to_csv(db_file, csv_file) 