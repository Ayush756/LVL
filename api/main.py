import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from api import (
   # find_nearest_road_node,
    calculate_road_distance,
    get_nearby_competitors,
    get_db_connection,
    find_closest_grid_point,
    get_5x5_grid_population,
    calculate_distance_score,
)
# --- App Setup ---
load_dotenv()
app = Flask(__name__)
CORS(app)


@app.route('/get_population', methods=['POST'])
def calculation():
    data = request.get_json()
    if not data or 'coords' not in data or 'userInputs' not in data:
        return jsonify({'error': 'Missing required keys: coords or userInputs'}), 400

    coords = data['coords']
    user_inputs = data['userInputs']

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    lng = coords['lng']
    lat = coords['lat']

    center_grid_point = find_closest_grid_point(coords['lng'], coords['lat'], cur)

    if center_grid_point:
        influenced_population_5x5 = get_5x5_grid_population(
            center_grid_point['grid_row'], center_grid_point['grid_col'], cur
        )
        closest_point_population = center_grid_point['population']
    else:
        influenced_population_5x5 = 0
        closest_point_population = 0

    print(influenced_population_5x5)
    print(closest_point_population)

calculation()