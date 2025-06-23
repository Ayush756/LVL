import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask App
app = Flask(__name__)
# Enable CORS for all routes, allowing requests from your React frontend
CORS(app)

# --- Database Connection Function ---
# A helper function to connect to the PostgreSQL database
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="localventurelens_db",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD']
    )
    return conn


# --- API Routes ---

# Basic test route to check if the API is running
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

# The following lines are useful for running the app directly with `python api.py`
# but are not necessary when using `flask run`.
if __name__ == '__main__':
    app.run(debug=True)