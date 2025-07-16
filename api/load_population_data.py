import os
import csv
import psycopg2
from dotenv import load_dotenv

def get_db_connection():
    """Connects to the database using credentials from .env file."""
    load_dotenv()
    conn = psycopg2.connect(
        host="localhost",
        database="LVL",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD']
    )
    return conn

def load_data():
    """Reads the CSV and inserts data into the population_grid table."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Clear the table before loading to avoid duplicates if run multiple times
    print("Clearing existing data from population_grid table...")
    cur.execute("TRUNCATE TABLE population_grid RESTART IDENTITY;")

    csv_file_path = 'POP_count_gridwise.csv'
    print(f"Reading data from {csv_file_path}...")

    with open(csv_file_path, mode='r') as f:
        reader = csv.DictReader(f)
        
        insert_query = """
            INSERT INTO population_grid (grid_row, grid_col, latitude, longitude, population, geom)
            VALUES (
                %(row)s, 
                %(col)s, 
                %(latitude)s, 
                %(longitude)s, 
                %(population)s, 
                ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s), 4326)
            );
        """
        
        # Use psycopg2's executemany for efficient batch inserting
        # We need to convert the reader object to a list first
        data_to_insert = list(reader)
        cur.executemany(insert_query, data_to_insert)

    # Commit the transaction to make the changes permanent
    conn.commit()
    
    print(f"Successfully loaded {cur.rowcount} records into the population_grid table.")

    # Close the cursor and connection
    cur.close()
    conn.close()

if __name__ == '__main__':
    load_data()