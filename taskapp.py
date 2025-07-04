import os
import mysql.connector
from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Helper funcion to close connections
def close_resources(conn, cur):
    if cur:
        cur.close()
    if conn:
        conn.close()

def get_db_connection():
    """Connects to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=os.getenv("MYSQL_PORT"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB")
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")

@app.route('/api/test')
def test_connection():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('SELECT VERSION();')
            db_version = cur.fetchone()
            close_resources(conn, cur)
            return jsonify({"message": "MySQL connection successful!", "version": db_version})
        except Exception as e:
            close_resources(conn, None)
            return jsonify({"error": f"MySQL query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to MySQL"}), 500

if __name__ == '__main__':
    app.run(debug=True)