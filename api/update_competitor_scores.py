import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

def get_db_connection():
    load_dotenv()
    return psycopg2.connect(
        host="localhost",
        database="LVL",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD']
    )

def calculate_competitor_attractiveness(cost, capacity, variety):
    """
    Calculates attractiveness based on cost, capacity, and variety.
    THIS IS THE FORMULA FROM YOUR main.py file.
    """
    # Using float to handle potential decimals in variety
    cost = float(cost) if cost is not None else 0
    capacity = float(capacity) if capacity is not None else 0
    variety = float(variety) if variety is not None else 0
    
    # Formula: attractiveness = cost*10 + varieties*20 + capacities*3 + amenities*5
    # We will assume a default of 5 amenities for all competitors.
    amenities = 5
    attractiveness = (cost * 10) + (variety * 20) + (capacity * 3) + (amenities * 5)
    return round(attractiveness, 2)

def update_scores():
    """Fetches competitors, recalculates their attractiveness, and updates the DB."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        print("Fetching all competitors from the database...")
        cur.execute("SELECT id, cost, capacity, variety FROM competitors;")
        competitors = cur.fetchall()

        if not competitors:
            print("No competitors found in the database.")
            return

        updates_to_perform = []
        for comp in competitors:
            new_score = calculate_competitor_attractiveness(comp['cost'], comp['capacity'], comp['variety'])
            updates_to_perform.append((new_score, comp['id']))
            print(f"  - Competitor ID {comp['id']}: New Score = {new_score}")
        
        # Use psycopg2's executemany for an efficient bulk UPDATE
        update_query = "UPDATE competitors SET attractiveness_score = %s WHERE id = %s;"
        cur.executemany(update_query, updates_to_perform)
        
        conn.commit()
        print(f"\nSuccessfully updated the attractiveness_score for {len(updates_to_perform)} competitors.")

    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    update_scores()