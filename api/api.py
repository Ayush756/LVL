import os
import random
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import numpy as np

# --- Import your analysis functions ---
from analysis.model import huff_model
from analysis.scoring import weighted_score
from analysis.normStd import min_max_scale
from analysis.ahp import ahp_weights

# --- App Setup & DB Connection (unchanged) ---
load_dotenv(); app = Flask(__name__)
CORS(app)
def get_db_connection():
    return psycopg2.connect(host="localhost", database="LVL", user=os.environ['DB_USERNAME'], password=os.environ['DB_PASSWORD'])

# --- Helper Functions ---
def find_closest_grid_point(lng, lat, cur):
    query = "SELECT grid_row, grid_col, population FROM population_grid ORDER BY geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326) LIMIT 1;"
    cur.execute(query, (lng, lat)); return cur.fetchone()

def get_5x5_grid_population(center_row, center_col, cur):
    row_min, row_max = center_row - 2, center_row + 2; col_min, col_max = center_row - 2, center_col + 2
    query = "SELECT SUM(population) as total_population FROM population_grid WHERE grid_row BETWEEN %s AND %s AND grid_col BETWEEN %s AND %s;"
    cur.execute(query, (row_min, row_max, col_min, col_max)); result = cur.fetchone()
    return result['total_population'] if result and result['total_population'] is not None else 0

def find_nearest_road_node(lng, lat, cur):
    query = "SELECT id FROM ways_vertices_pgr ORDER BY the_geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326) LIMIT 1;"
    cur.execute(query, (lng, lat)); return cur.fetchone()

def calculate_road_distance(start_node_id, end_node_id, cur):
    query = "SELECT SUM(cost) * 111139 AS distance_in_meters FROM pgr_dijkstra('SELECT gid AS id, source, target, cost, reverse_cost FROM ways', %s, %s, directed := false);"
    cur.execute(query, (start_node_id, end_node_id)); result = cur.fetchone()
    return result['distance_in_meters'] if result and result['distance_in_meters'] is not None else None

def get_population_stats(cur):
    """Gets the min and max 5x5 grid population values for dynamic normalization."""
    cur.execute("SELECT MIN(population) as min_pop, MAX(population) as max_pop FROM population_grid;")
    stats = cur.fetchone()
    # Estimate min/max for 5x5 grids. This is an approximation.
    # A more advanced method would pre-calculate all 5x5 sums.
    return {'min': stats['min_pop'] * 5, 'max': stats['max_pop'] * 25}

def calculate_accessibility_score(distance_to_road_meters):
    """
    Calculates accessibility score based on distance to the nearest road.
    Inverse relationship: 0m distance = score of 1.0 (100). 100m distance = score of 0.
    """
    # Normalize against a 0-100 meter range.
    normalized = 1 - min_max_scale([0, distance_to_road_meters, 100])[1]
    return normalized
def find_nearest_road_node(lng, lat, cur):
    """
    Finds the nearest road node and ALSO returns the direct distance to it in meters.
    The ST_Distance function with 'geography' type gives accurate meter distances.
    """
    query = """
        SELECT 
            id, 
            ST_Distance(
                the_geom::geography, 
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
            ) as dist_meters
        FROM ways_vertices_pgr
        ORDER BY the_geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
        LIMIT 1;
    """
    # We pass the coordinates twice because they are used in two places in the query
    cur.execute(query, (lng, lat, lng, lat))
    return cur.fetchone()
# --- The New, Powerful Report Generation Endpoint ---
@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    data = request.get_json()
    coords = data['coords']
    user_inputs = data['userInputs']

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # --- 1. DATA GATHERING (All DB operations are inside the 'try' block) ---
        cur.execute("SELECT name, latitude, longitude, attractiveness_score FROM competitors;")
        competitors = cur.fetchall()
        
        center_grid_point = find_closest_grid_point(coords['lng'], coords['lat'], cur)
        population_5x5 = get_5x5_grid_population(center_grid_point['grid_row'], center_grid_point['grid_col'], cur) if center_grid_point else 0
        population_stats = get_population_stats(cur)
        
        start_node_result = find_nearest_road_node(coords['lng'], coords['lat'], cur)
        start_node = start_node_result['id'] if start_node_result else None
        distance_to_road = start_node_result['dist_meters'] if start_node_result else 100.0

        # --- 2. CALCULATE THE FOUR FACTOR SCORES (Also inside the 'try' block) ---
        
        # Factor 1: DEMOGRAPHICS
        pop_range = population_stats['max'] - population_stats['min']
        score_demographic = (population_5x5 - population_stats['min']) / pop_range if pop_range > 0 else 0.5
        score_demographic = np.clip(score_demographic, 0, 1)

        # Factor 2: PROXIMITY (to Landmarks)
        key_destinations = {
            "28 Kilo highway": {"lat": 27.624931, "lng": 85.541031, "weight": 2},
            "KU gate":         {"lat": 27.620517, "lng": 85.538328, "weight": 3},
            "LMTC road":       {"lat": 27.618500, "lng": 85.543284, "weight": 1},
            "Gamya side":      {"lat": 27.616308, "lng": 85.539899, "weight": 1},
            "Khadpu":          {"lat": 27.615042, "lng": 85.532427, "weight": 1},
            "Banepa side":     {"lat": 27.625653, "lng": 85.531601, "weight": 1}
        }
        weighted_total_distance = 0
        if start_node:
            for dest_data in key_destinations.values():
                dest_node_result = find_nearest_road_node(dest_data['lng'], dest_data['lat'], cur)
                if dest_node_result:
                    dist_m = calculate_road_distance(start_node, dest_node_result['id'], cur)
                    weighted_total_distance += (dist_m if dist_m is not None else 5000) * dest_data['weight']
        score_proximity = 1 - min_max_scale([10000, weighted_total_distance, 50000])[1]

        # Factor 3: MARKET SHARE (Huff Model)
        candidate_attractiveness = (user_inputs['cost'] * 10) + (user_inputs['variety'] * 20) + (user_inputs['capacity'] * 3) + (5*5)
        comp_attractiveness = [c['attractiveness_score'] for c in competitors]
        comp_distances_km = []
        if start_node:
            for comp in competitors:
                comp_node_result = find_nearest_road_node(comp['longitude'], comp['latitude'], cur)
                if comp_node_result:
                    dist = calculate_road_distance(start_node, comp_node_result['id'], cur)
                    comp_distances_km.append(dist / 1000 if dist is not None else 10.0)
        all_attractiveness = np.array([candidate_attractiveness] + comp_attractiveness)
        all_distances = np.array([0.01] + comp_distances_km)
        huff_scores = huff_model(all_attractiveness, score_proximity, beta=2)
        score_market_share = huff_scores[0]

        # Factor 4: ACCESSIBILITY (Distance to Road)
        score_accessibility = calculate_accessibility_score(distance_to_road)

        # --- 3. FINAL SCORE CALCULATION ---
        #demographic, proximity, market share, and accessibility scores are combined using AHP weights.
        pairwise_matrix = [
            [1,   3,   2,   4],
            [1/3, 1,   1/3, 2],
            [1/2, 3,   1,   3],
            [1/4, 1/2, 1/3, 1]
        ]
        weights = ahp_weights(pairwise_matrix)
        
        factor_scores = [score_demographic, score_proximity, score_market_share, score_accessibility]
        final_score = weighted_score(factor_scores, weights.tolist())

    finally:
        # This block ensures the connection is always closed, no matter what.
        cur.close()
        conn.close()

    # The final return statement is OUTSIDE the try...finally block.
    return jsonify({
        "final_score": round(final_score * 100, 2),
        "factors": {
            "labels": ["Demographic Fit", "Landmark Proximity", "Market Share", "Road Accessibility"],
            "scores": [round(s * 100) for s in factor_scores]
        },
        "key_metrics": {
            "population_influenced": int(population_5x5),
            "distance_to_road_m": round(distance_to_road, 1)
        }
    })