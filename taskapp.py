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
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
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
                    return redirect(url_for('dashboard'))
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
    if request.method == 'POST':
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

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    print('USER:', session["user_id"])

    user_id = session["user_id"]

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT * FROM (
                SELECT u.name, u.username FROM users AS u
                    INNER JOIN friends AS f ON u.id = f.friend2
                    WHERE f.friend1 = %s
                UNION ALL
                SELECT u2.name, u2.username FROM users AS u2
                    INNER JOIN friends AS f2 ON u2.id = f2.friend1
                    WHERE f2.friend2 = %s) AS all_friends
                ORDER BY name;
            """, (user_id, user_id))
            friends_list = cur.fetchall()
            close_resources(conn, cur)
            return render_template("dashboard.html", friends=friends_list)
        except mysql.connector.Error as err:
            close_resources(conn, cur)
            flash(str(err), "danger")
    else:
        flash("Database connection failed", "danger")
    return render_template("dashboard.html")

@app.route("/add")
def add():
    user_id = session["user_id"]
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            #get incoming requests

            cur.execute("""
                SELECT fr.request_id, u.name, u.username FROM users AS u
                    INNER JOIN friend_requests AS fr ON u.id = fr.made_by
                    WHERE fr.made_for = %s AND fr.status = 'Pending';
            """, (user_id,))
            incoming_list = cur.fetchall()
            #get pending requests
            cur.execute("""
                SELECT u.name, u.username FROM users AS u
                    INNER JOIN friend_requests AS fr ON u.id = fr.made_for
                    WHERE fr.made_by = %s AND fr.status = 'Pending';
            """, (user_id,))
            pending_list = cur.fetchall()
            close_resources(conn, cur)
            return render_template("add.html", pending=pending_list, incoming = incoming_list)
        except mysql.connector.Error as err:
            close_resources(conn, cur)
            flash(str(err), "danger")
    else:
        flash("Database connection failed", "danger")
    return render_template("add.html")

@app.route("/respond_request", methods=['POST'])
def respond():
    user_id = session["user_id"]
    request_id = request.form.get("request")
    action = request.form.get("action")
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT made_by FROM friend_requests WHERE request_id = %s;
            """, (request_id,))
            from_user = cur.fetchone()[0]

            if action == "accept":
                # Insert into friends table
                cur.execute("""
                    INSERT INTO friends (friend1, friend2) VALUES (%s, %s);
                """, (user_id, from_user))
                #update request
                cur.execute("""
                    UPDATE friend_requests SET status = 'Approved', date_reviewed = NOW() WHERE request_id = %s;
                """, (request_id,))
            elif action == "deny":
                # deny request
                cur.execute("""
                    UPDATE friend_requests SET status = 'Denied', date_reviewed = NOW() WHERE request_id = %s;
                """, (request_id,))
            conn.commit()
            close_resources(conn, cur)


        except mysql.connector.Error as err:
            close_resources(conn, cur)
            flash(str(err), "danger")
    else:
        flash("Database connection failed", "danger")
    return redirect(url_for('add'))

@app.route("/send_friend_request", methods=["POST"])
def send_friend_request():
    user_id = session["user_id"]
    username = request.form.get("username")
    conn = get_db_connection()
    cur = conn.cursor()
    if conn:
        try:
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cur.fetchone()

            if not result:
                flash("User not found.", "danger")
                return redirect(url_for("add"))

            friend_id = result[0]
            if friend_id == user_id:
                flash("You cannot add yourself.", "danger")
                return redirect(url_for("add"))
            
            cur.execute("""
                SELECT 1 FROM friends
                    WHERE (friend1 = %s AND friend2 = %s)
                    OR (friend1 = %s AND friend2 = %s)
            """, (user_id, friend_id, friend_id, user_id))
            if cur.fetchone():
                flash("Friend already exists.", "danger")
                return redirect(url_for("add"))

            cur.execute("""
                SELECT 1 FROM friend_requests
                    WHERE (made_by = %s AND made_for = %s AND status = 'Pending')
                    OR (made_by = %s AND made_for = %s AND status = 'Pending');
            """, (user_id, friend_id, friend_id, user_id))
            if cur.fetchone():
                flash("Friend request exists and is pending.", "danger")
                return redirect(url_for("add"))

            cur.execute("""
                INSERT INTO friend_requests(made_by, made_for, date_created) VALUES
                    (%s, %s, NOW());
            """,(user_id, friend_id))
            conn.commit()
            conn.close()
            flash("Friend request sent!", "success")
        except mysql.connector.Error as err:
            close_resources(conn, cur)
            flash(str(err), "danger")
    else:
        flash("Database connection failed", "danger")
    return redirect(url_for('add'))


if __name__ == '__main__':
    app.run(debug=True)