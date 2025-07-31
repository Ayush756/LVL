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
    """
    Calculates an attractiveness score based on capacity and variety.
    Logic: Normalize both values to a 0-1 scale, then apply weights.
    - Capacity is weighted 60%
    - Variety is weighted 40%
    """
    # Normalize capacity (assuming max capacity is ~100 people for this area)
    capacity_score = min(capacity / 100.0, 1.0) 

    # Normalize variety (assuming max variety is ~50 distinct items)
    variety_score = min(variety / 50.0, 1.0)
    
    # Apply weights and scale to 100
    attractiveness = ((capacity_score * 0.6) + (variety_score * 0.4)) * 100
    return round(attractiveness, 2)

def load_data():
    """Reads Capacity.csv, generates data, calculates score, and loads into DB."""
    conn = get_db_connection()
    cur = conn.cursor()

    print("Clearing existing data from competitors table...")
    cur.execute("TRUNCATE TABLE competitors RESTART IDENTITY;")

    csv_file_path = 'Capacity.csv'
    print(f"Reading data from {csv_file_path}...")

    with open(csv_file_path, mode='r') as f:
        reader = csv.DictReader(f)
        
        insert_query = """
            INSERT INTO competitors (name, latitude, longitude, cost, variety, capacity, attractiveness_score, geom)
            VALUES (%s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
        """
        
        records_to_insert = []
        for row in reader:
            # Generate reasonable random data for each competitor
            # (In a real project, this data would be collected)
            cost = random.randint(150, 500)      # e.g., Avg. price
            variety = random.randint(10, 45)     # e.g., Number of menu items
            capacity = random.randint(15, 80)    # e.g., Seating capacity

            # Calculate the attractiveness score
            attractiveness = calculate_attractiveness(capacity, variety)
            
            records_to_insert.append((
                row['name'], float(row['lat']), float(row['long']),
                cost, variety, capacity, attractiveness,
                float(row['long']), float(row['lat'])
            ))

        # Bulk insert all records efficiently
        cur.executemany(insert_query, records_to_insert)

    conn.commit()
    print(f"Successfully loaded {cur.rowcount} records into the competitors table.")
    cur.close()
    conn.close()

if __name__ == '__main__':
    load_data()