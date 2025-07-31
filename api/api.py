import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# --- App Setup ---
load_dotenv()
app = Flask(__name__)
CORS(app)

# --- DB Connection ---
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="LVL",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD']
    )

# --- REUSABLE HELPER FUNCTIONS (ALL NOW ACCEPT 'cur') ---

def find_nearest_road_node(lng, lat, cur):
    """Finds the ID of the nearest road node. Takes a cursor as an argument."""
    query = """
        SELECT id FROM ways_vertices_pgr
        ORDER BY the_geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
        LIMIT 1;
    """
    cur.execute(query, (lng, lat))
    return cur.fetchone()

def calculate_road_distance(start_node_id, end_node_id, cur):
    """Calculates road distance. Takes a cursor as an argument."""
    query = """
        SELECT SUM(cost) * 111139 AS distance_in_meters
        FROM pgr_dijkstra(
            'SELECT gid AS id, source, target, cost, reverse_cost FROM ways',
            %s, %s, directed := false
        );
    """
    cur.execute(query, (start_node_id, end_node_id))
    result = cur.fetchone()
    return result['distance_in_meters'] if result and result['distance_in_meters'] is not None else None

def get_nearby_competitors(lng, lat, radius_meters, cur):
    """Gets all competitors from the DB within a given radius."""
    query = """
        SELECT name, attractiveness_score, latitude, longitude
        FROM competitors
        WHERE ST_DWithin(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s);
    """
    cur.execute(query, (lng, lat, radius_meters))
    return cur.fetchall()

def calculate_attractiveness(capacity, variety):
    """Calculates attractiveness score. This is pure math, no DB needed."""
    capacity_score = min(capacity / 100.0, 1.0) 
    variety_score = min(variety / 50.0, 1.0)
    attractiveness = ((capacity_score * 0.6) + (variety_score * 0.4)) * 100
    return round(attractiveness, 2)

def find_closest_grid_point(lng, lat, cur):
    """Finds the single closest population grid point. Takes a cursor."""
    query = """
        SELECT grid_row, grid_col, population
        FROM population_grid
        ORDER BY geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
        LIMIT 1;
    """
    cur.execute(query, (lng, lat))
    return cur.fetchone()

def get_5x5_grid_population(center_row, center_col, cur):
    """Calculates the total population in a 5x5 grid. Takes a cursor."""
    row_min, row_max = center_row - 2, center_row + 2
    col_min, col_max = center_col - 2, center_col + 2
    query = """
        SELECT SUM(population) as total_population
        FROM population_grid
        WHERE grid_row BETWEEN %s AND %s AND grid_col BETWEEN %s AND %s;
    """
    cur.execute(query, (row_min, row_max, col_min, col_max))
    result = cur.fetchone()
    return result['total_population'] if result and result['total_population'] is not None else 0

def calculate_distance_score(start_lng, start_lat, cur):
    """
    Calculates a weighted distance score based on proximity to fixed key locations.
    Lower score is better.
    """
    # These are fixed points of interest with their weights
    key_locations = {
         "28 Kilo highway":    { "lat": 27.624931, "lng": 85.541031,"weight":2 },
        "LMTC road":     { "lat": 27.618500, "lng": 85.543284,"weight":1 },
        "Gamya side":     { "lat": 27.616308, "lng": 85.539899,"weight":1 },
        "Khadpu":  { "lat": 27.615042, "lng": 85.532427,"weight":1 },
        "Banepa side":           { "lat": 27.625653, "lng": 85.531601,"weight":1 },
        "KU gate":  { "lat": 27.620517, "lng": 85.538328,"weight":3 }
    }
    
    start_node_result = find_nearest_road_node(start_lng, start_lat, cur)
    if not start_node_result:
        return 0 
    start_node = start_node_result['id']

    total_weighted_distance = 0
    for loc_name, data in key_locations.items():
        loc_node_result = find_nearest_road_node(data['lng'], data['lat'], cur)
        if loc_node_result:
            distance_m = calculate_road_distance(start_node, loc_node_result['id'], cur)
            if distance_m:
                total_weighted_distance += (distance_m / 1000) * data['weight']
                
    return round(total_weighted_distance, 2)

# --- FINAL UNIFIED REPORT ENDPOINT ---

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    data = request.get_json()
    coords = data['coords']
    user_inputs = data['userInputs']

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # --- 1. Population Analysis ---
        center_grid_point = find_closest_grid_point(coords['lng'], coords['lat'], cur)
        population_analysis = {
            "influenced_population_5x5": get_5x5_grid_population(
                center_grid_point['grid_row'], center_grid_point['grid_col'], cur
            ) if center_grid_point else 0,
            "closest_point_population": center_grid_point['population'] if center_grid_point else 0
        }

        # --- 2. Competitive Analysis (simpler) ---
        nearby_competitors = get_nearby_competitors(coords['lng'], coords['lat'], 1000, cur)
        user_attractiveness = calculate_attractiveness(user_inputs['capacity'], user_inputs['variety'])

        competitive_analysis = {
            "user_attractiveness": user_attractiveness,
            "competitor_count": len(nearby_competitors)
        }

        # --- 3. Distance Analysis (now independent) ---
        distance_score = calculate_distance_score(coords['lng'], coords['lat'], cur)

    finally:
        cur.close()
        conn.close()

    return jsonify({
        "population_analysis": population_analysis,
        "competitive_analysis": competitive_analysis,
        "distance_score": distance_score
    })