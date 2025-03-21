import sqlite3
import json
import os

# Connect to the SQLite database
db_path = 'mckinsey_data.db'  # Ensure this path is correct
if not os.path.exists(db_path):
    raise FileNotFoundError(f"The database file {db_path} does not exist.")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query to select all articles
cursor.execute("SELECT * FROM articles")  # Adjust the table name as needed
articles = cursor.fetchall()

# Convert to JSON Lines format
output_file = 'mckinsey_data.jsonl'
with open(output_file, 'w') as jsonl_file:
    for article in articles:
        json_line = json.dumps({
            'id': article[0],  # Assuming the first column is the ID
            'title': article[1],  # Adjust based on your table structure
            'url': article[2],
            'description': article[3],
            'date_published': article[4],
            'article_type': article[5]
        })
        jsonl_file.write(json_line + '\n')

# Close the database connection
conn.close()

print(f"Successfully converted database to {output_file} in JSON Lines format.")
