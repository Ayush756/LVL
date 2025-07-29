import os
import csv
import psycopg2
from dotenv import load_dotenv

def get_db_connection():
    """Connects to the database using credentials from .env file."""
    load_dotenv()
    conn = psycopg2.connect(
        host="localhost",
        database="localventurelens_db",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD']
    )
    return conn

def load_data():
    """Reads the CSV and inserts data into the competitors table."""
    conn = get_db_connection()
    cur = conn.cursor()

    # This command clears the table before loading. This is useful because
    # it prevents creating duplicate entries if you run the script multiple times.
    print("Clearing existing data from competitors table...")
    cur.execute("TRUNCATE TABLE competitors RESTART IDENTITY;")

    csv_file_path = 'comp_data.csv'
    print(f"Reading data from {csv_file_path}...")

    with open(csv_file_path, mode='r') as f:
        # Using DictReader is great because we can access columns by name
        reader = csv.DictReader(f)
        
        # Note: The PostGIS ST_MakePoint function takes longitude first, then latitude.
        insert_query = """
            INSERT INTO competitors (name, latitude, longitude, geom)
            VALUES (
                %(name)s, 
                %(lat)s, 
                %(lon)s, 
                ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)
            );
        """
        
        # executemany is an efficient way to insert many rows at once
        data_to_insert = list(reader)