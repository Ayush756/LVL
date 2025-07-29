import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# --- App and DB Setup ---
load_dotenv()
app = Flask(__name__)
CORS(app)

def get_db_connection():
    # This function is unchanged
    if 'DATABASE_URL' in os.environ:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
    else:
        conn = psycopg2.connect(
            host="localhost",
            database="LVL", # Make sure this matches your DB name
            user=os.environ['DB_USERNAME'],
            password=os.environ['DB_PASSWORD']
        )
    return conn

@app.route('/api/test')
def test_endpoint():
    return jsonify({"message": "Hello from your Flask API!"})


# Database connection test route
@app.route('/api/db_test')
def db_test():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT version();')
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"db_version": db_version[0]})
    except Exception as e:
        # Return the actual error for easier debugging
        return jsonify({"error": f"Database connection failed: {e}"}), 500

def find_closest_grid_point(lng, lat):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT grid_row, grid_col, population
        FROM population_grid
        ORDER BY geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
        LIMIT 1;
    """
    try:
        cur.execute(query, (lng, lat))
        closest_point = cur.fetchone()
    finally:
        cur.close()
        conn.close()
    return closest_point

def get_5x5_grid_population(center_row, center_col):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    row_min, row_max = center_row - 2, center_row + 2
    col_min, col_max = center_col - 2, center_col + 2
    query = """
        SELECT SUM(population) as total_population
        FROM population_grid
        WHERE grid_row BETWEEN %s AND %s AND grid_col BETWEEN %s AND %s;
    """
    try:
        cur.execute(query, (row_min, row_max, col_min, col_max))
        result = cur.fetchone()
    finally:
        cur.close()
        conn.close()
    return result['total_population'] if result and result['total_population'] is not None else 0

# Route to handle location data from the map
@app.route('/api/location', methods=['POST'])
def handle_location():
    # Get the JSON data sent from the frontend
    data = request.get_json()
    if not data or 'lat' not in data or 'lng' not in data:
        return jsonify({"error": "Missing coordinates"}), 400

    lat = data['lat']
    lng = data['lng']

    # --- THIS IS WHERE YOU WILL DO YOUR BUSINESS VIABILITY LOGIC ---
    # For now, we'll just print it to the backend terminal to prove it works.
    print(f"SUCCESS: Received coordinates from frontend -> Latitude: {lat}, Longitude: {lng}")

    # Send a response back to the frontend
    return jsonify({
        "status": "success",
        "message": f"Backend received coordinates: ({lat}, {lng})"
    }), 200
# --- Reusable Geospatial Functions (unchanged) ---

def find_nearest_road_node(lng, lat):
    """Finds the ID of the nearest road network node (intersection) to a given point."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT id FROM ways_vertices_pgr
        ORDER BY the_geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
        LIMIT 1;
    """
    try:
        cur.execute(query, (lng, lat))
        nearest_node = cur.fetchone()
    finally:
        cur.close()
        conn.close()
    
    return nearest_node['id'] if nearest_node else None

def calculate_road_distance(start_node_id, end_node_id):
    """Calculates the shortest road distance between two node IDs using pgRouting."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT SUM(cost) * 111139 AS distance_in_meters
        FROM pgr_dijkstra(
            'SELECT gid AS id, source, target, cost, reverse_cost FROM ways',
            %s, %s, directed := false
        );
    """
    try:
        cur.execute(query, (start_node_id, end_node_id))
        result = cur.fetchone()
    finally:
        cur.close()
        conn.close()

    return result['distance_in_meters'] if result and result['distance_in_meters'] is not None else None

# --- NEW Proximity Analysis Logic ---

@app.route('/api/analyze_population', methods=['POST'])
def analyze_population():
    clicked_point = request.get_json()
    lat, lng = clicked_point['lat'], clicked_point['lng']
    center_grid_point = find_closest_grid_point(lng, lat)
    if not center_grid_point:
        return jsonify({"error": "No population data found near the selected location."}), 404
    closest_point_population = center_grid_point['population']
    total_influenced_population = get_5x5_grid_population(center_grid_point['grid_row'], center_grid_point['grid_col'])
    return jsonify({
        "closest_point_population": closest_point_population,
        "influenced_population_5x5": total_influenced_population
    })

@app.route('/api/analyze_proximity', methods=['POST'])
def analyze_proximity():
    # Get the user's clicked starting point
    start_point = request.get_json()
    start_lat = start_point['lat']
    start_lng = start_point['lng']

    # --- 1. DEFINE YOUR 6 DESTINATION POINTS ---
    # In a real app, this would come from a database query.
    # Replace these with real coordinates for schools, hospitals, markets, etc.
    destinations = {
        "28 Kilo highway":    { "lat": 27.624931, "lng": 85.541031,"weight":2 },
        "LMTC road":     { "lat": 27.618500, "lng": 85.543284,"weight":1 },
        "Gamya side":     { "lat": 27.616308, "lng": 85.539899,"weight":1 },
        "Khadpu":  { "lat": 27.615042, "lng": 85.532427,"weight":1 },
        "Banepa side":           { "lat": 27.625653, "lng": 85.531601,"weight":1 },
        "KU gate":  { "lat": 27.620517, "lng": 85.538328,"weight":3 }
    }

    # Find the nearest road node for our starting point
    start_node = find_nearest_road_node(start_lng, start_lat)
    if not start_node:
        return jsonify({"error": "Could not find a nearby road for your starting point."}), 400

    weighted_distance_sum = 0
    valid_distances = []

    for name, data in destinations.items():
        dest_node = find_nearest_road_node(data['lng'], data['lat'])
        if dest_node:
            distance_meters = calculate_road_distance(start_node, dest_node)
            if distance_meters is not None:
                distance_km = distance_meters / 1000
                valid_distances.append(distance_km)
                weighted_distance_sum += distance_km * data['weight']

    # "Range of Influence" is the max distance to any key point
    range_of_influence_km = max(valid_distances) if valid_distances else 0

    # 3. NEW JSON RESPONSE
    return jsonify({
        "range_of_influence_km": round(range_of_influence_km, 2),
        "accessibility_score": round(weighted_distance_sum, 2)
    })
