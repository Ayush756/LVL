import os
from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app) # This will allow requests from your React app

# Function to get a database connection
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="LVL_db",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD']
    )
    return conn

@app.route('/api/test')
def test_endpoint():
    return jsonify({"message": "Hello from your Flask API!"})

@app.route('/api/db_test')
def db_test():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT version();')
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"db_version": db_version})
    except Exception as e:
        return jsonify({"error": str(e)}), 500