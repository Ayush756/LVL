import os
import csv
import psycopg2
import random
from dotenv import load_dotenv

def get_db_connection():
    load_dotenv()
    return psycopg2.connect(
        host="localhost",
        database="LVL",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD']
    )

def calculate_attractiveness(capacity, variety):
    """Calculates an attractiveness score based on capacity and variety."""
    capacity_score = min(capacity / 100.0, 1.0) 
    variety_score = min(variety / 50.0, 1.0)
    attractiveness = ((capacity_score * 0.6) + (variety_score * 0.4)) * 100
    return round(attractiveness, 2)

def load_data():
    """
    Reads comp_data.csv, generates data, calculates score, and loads into DB.
    THIS SCRIPT IS CORRECTED FOR THE 'lat' and 'lon' a column names.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    print("--- CORRECTED SCRIPT ---")
    print("Clearing existing data from competitors table...")
    cur.execute("TRUNCATE TABLE competitors RESTART IDENTITY;")

    csv_file_path = 'comp_data.csv' # <-- Corrected file name
    print(f"Reading data from {csv_file_path}...")

    with open(csv_file_path, mode='r') as f:
        reader = csv.DictReader(f)
        
        insert_query = """
            INSERT INTO competitors (name, latitude, longitude, cost, variety, capacity, attractiveness_score, geom)
            VALUES (%s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
        """
        
        records_to_insert = []
        for row in reader:
            cost = random.randint(150, 500)
            variety = random.randint(10, 45)
            capacity = random.randint(15, 80)
            attractiveness = calculate_attractiveness(capacity, variety)
            
            # Use the correct column names from your CSV: 'lat' and 'lon'
            records_to_insert.append((
                row['name'], float(row['lat']), float(row['lon']),
                cost, variety, capacity, attractiveness,
                float(row['lon']), float(row['lat'])
            ))

        cur.executemany(insert_query, records_to_insert)

    conn.commit()
    print(f"Successfully loaded {cur.rowcount} records into the competitors table.")
    cur.close()
    conn.close()

if __name__ == '__main__':
    load_data()