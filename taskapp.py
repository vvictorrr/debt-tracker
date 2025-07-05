import os
import mysql.connector
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY") or 'dev'


app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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

@app.route('/')
def index():
    #if "user_id" in session:
    #    return redirect("/dashboard")
    return redirect("/login")

@app.route('/login', methods=['GET', 'POST'])
def login():
    print('login')
    session.clear()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print('submitted')
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, password))
                user = cur.fetchone()
                close_resources(conn, cur)
                if user:
                    session["user_id"] = user[0]
                    flash("Logged in successfully.", "success")
                    return redirect(('dashboard.html'))
                else:
                    flash("Invalid username or password", "danger")
            except mysql.connector.Error as err:
                close_resources(conn, cur)
                flash(str(err), "danger")
        else:
            flash("Database connection failed", "danger")
    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    print("hello")
    if request.method == 'POST':
        print('hi2')
        display_name = request.form.get('display_name')
        username = request.form.get('username')
        password = request.form.get('password')
        print(display_name, username, password)

        if not username or not password or not display_name:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()

                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                existing = cur.fetchone()
                if existing:
                    close_resources(conn, cur)
                    flash("Username already taken.", "danger")
                    return render_template("register.html")

                cur.execute("INSERT INTO users (name, username, password) VALUES (%s, %s, %s)", (display_name, username, password))
                conn.commit()
                close_resources(conn, cur)

                flash("Registered successfully. Please log in.", "success")
                return redirect(url_for('login'))

            except mysql.connector.Error as err:
                close_resources(conn, cur)
                flash(str(err), "danger")
        else:
            flash("Database connection failed", "danger")
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    return "Welcome to the dashboard!"

if __name__ == '__main__':
    app.run(debug=True)