import os
import psycopg2
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
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
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
                SELECT u.id, u.name, u.username, f1.owes AS you_owe, f2.owes AS they_owe_you
                    FROM users AS u
                        INNER JOIN friends AS f1 ON u.id = f1.friend2 AND f1.friend1 = %s
                        LEFT JOIN friends AS f2 ON f2.friend1 = u.id AND f2.friend2 = %s
                    ORDER BY u.name;
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

@app.route("/pay_off", methods=["POST"])
def pay_off():
    user_id = session.get("user_id")
    friend_id = request.form.get("friend_id")

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE friends SET owes = 0
                WHERE friend1 = %s AND friend2 = %s
            """, (user_id, friend_id))
            cur.execute("""
                INSERT INTO payment_logs (done_by, done_to, amount, time_occurred, action_type) VALUES:
                (%s, %s, %s, NOW(), 'pay_off');
            """, (user_id, friend_id, amount))
            conn.commit()
            close_resources(conn, cur)
            flash("Debt paid off!", "success")
        except mysql.connector.Error as err:
            flash(str(err), "danger")
            close_resources(conn, cur)
    else:
        flash("Database connection failed.", "danger")

    return redirect(url_for("dashboard"))

@app.route("/forgive_debt", methods=["POST"])
def forgive_debt():
    user_id = session.get("user_id")
    friend_id = request.form.get("friend_id")
    amount = request.form.get("amount")

    try:
        amount = float(amount)
        if amount <= 0:
            flash("Amount must be positive.", "warning")
            return redirect(url_for("dashboard"))
    except ValueError:
        flash("Invalid amount.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Fetch how much they currently owe
            cur.execute("""
                SELECT owes FROM friends WHERE friend1 = %s AND friend2 = %s
            """, (friend_id, user_id))
            result = cur.fetchone()

            if not result:
                flash("No debt to forgive.", "warning")
            else:
                current_owed = result[0]
                if amount > current_owed:
                    flash(f"You can't forgive more than the current debt (${current_owed:.2f}).", "danger")
                else:
                    new_amount = max(0.0, current_owed - amount)
                    cur.execute("""
                        UPDATE friends SET owes = %s
                        WHERE friend1 = %s AND friend2 = %s
                    """, (new_amount, friend_id, user_id))
                    cur.execute("""
                        INSERT INTO payment_logs (done_by, done_to, amount, time_occurred, action_type) VALUES:
                        (%s, %s, %s, NOW(), 'forgive');
                    """, (user_id, friend_id, amount))
                    conn.commit()
                    flash(f"Forgave ${min(current_owed, amount):.2f}.", "success")

        except mysql.connector.Error as err:
            flash(str(err), "danger")
        finally:
            close_resources(conn, cur)
    else:
        flash("Database connection failed.", "danger")

    return redirect(url_for("dashboard"))

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
def respond_request():
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
                cur.execute("""
                    INSERT INTO friends (friend1, friend2) VALUES (%s, %s);
                """, (from_user, user_id))
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
            """, (user_id, friend_id))
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
            close_resources(conn, cur)
            flash("Friend request sent!", "success")
        except mysql.connector.Error as err:
            close_resources(conn, cur)
            flash(str(err), "danger")
    else:
        flash("Database connection failed", "danger")
    return redirect(url_for('add'))

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    user_id = session.get('user_id')
    conn = get_db_connection()
    if conn:
        cur = conn.cursor(dictionary=True)

        if request.method == 'GET':
            try:
                # Fetch friends for selection
                cur.execute("""
                    SELECT u.id, u.name, u.username FROM users AS u
                        INNER JOIN friends AS f ON u.id = f.friend2
                        WHERE f.friend1 = %s
                    ORDER BY u.name;
                """, (user_id,))
                friends = cur.fetchall()

                #past payments
                cur.execute("""
                    SELECT * FROM (
                        SELECT p.payment_id, 'You' AS paid_by, p.total, 0.0 AS you_owed, p.description, p.date_paid
                            FROM payments p
                            WHERE p.paid_by = %s
                        UNION
                        SELECT p.payment_id, CONCAT(u.name, ' (', u.username, ')'), p.total, d.amount_owed, p.description, p.date_paid
                            FROM payments p
                                INNER JOIN debts d ON p.payment_id = d.payment
                                INNER JOIN users AS u ON p.paid_by = u.id
                            WHERE d.debtor = %s) AS all_payments
                    ORDER BY date_paid DESC;
                    """, (user_id, user_id))
                
                past_payments = cur.fetchall()
                close_resources(conn, cur)
            except mysql.connector.Error as err:
                flash(str(err), 'danger')
                friends = []
                close_resources(conn, cur)
            return render_template('payment.html', friends=friends, past_payments=past_payments)
        elif request.method == 'POST':
            total = request.form.get('total', type=float)
            description = request.form.get('description', '').strip()
            debts = []
            sum_debts = 0.0
            # Collect debts from form inputs
            for key, val in request.form.items():
                if key.startswith('debtor_'):
                    debtor_id = int(key.split('_')[1])
                    try:
                        amount = float(val)
                    except (TypeError, ValueError):
                        amount = 0.0
                    if amount > 0:
                        debts.append((debtor_id, amount))
                        sum_debts += amount
            
            if round(sum_debts, 2) > round(total, 2):
                close_resources(conn, cur)
                flash('Debtors cannot owe more than the total paid.', 'danger')
                return redirect(url_for('payment'))

            try:
                # Insert into payments
                cur.execute(
                    "INSERT INTO payments (paid_by, date_paid, total, description)"
                    " VALUES (%s, NOW(), %s, %s)",
                    (user_id, total, description)
                )
                conn.commit()
                payment_id = cur.lastrowid

                # Insert each debt record
                for debtor_id, amount in debts:
                    cur.execute(
                        "INSERT INTO debts (payment, debtor, amount_owed) VALUES (%s, %s, %s)",
                        (payment_id, debtor_id, amount)
                    )

                #debtor OWES payer
                #Update running debts
                cur.execute(""" SELECT * FROM friends """)
                all_debts = cur.fetchall()
                debt_map = {(row["friend1"], row["friend2"]): row["owes"] for row in all_debts}

                #cancel overlapping
                for debtor_id, amount in debts:
                    user_owes = debt_map.get((user_id, debtor_id), 0.0)
                    if user_owes >= amount:
                        cur.execute("""
                            UPDATE friends SET owes = %s
                            WHERE friend1 = %s AND friend2 = %s
                        """, (user_owes - amount, user_id, debtor_id))
                    else:
                        cur.execute("""
                            UPDATE friends SET owes = %s
                            WHERE friend1 = %s AND friend2 = %s
                        """, (0.0, user_id, debtor_id))
                        cur.execute("""
                            UPDATE friends SET owes = %s
                            WHERE friend1 = %s AND friend2 = %s
                        """, (amount - user_owes, debtor_id, user_id))
                
                #update debts
                conn.commit()
                cur.execute(""" SELECT * FROM friends """)
                all_debts = cur.fetchall()
                debt_map = {(row["friend1"], row["friend2"]): row["owes"] for row in all_debts}
                #transfer debts where possible
                transferred = True
                while transferred:
                    transferred = False
                    keys = list(debt_map.keys())

                    for (a, b) in keys:
                        ab_owes = debt_map.get((a, b), 0.0)
                        if ab_owes <= 0:
                            continue
                        for (x, c) in keys:
                            if x != b:
                                continue
                            bc_owes = debt_map.get((b, c), 0.0)
                            if bc_owes <= 0 or a == c:
                                continue

                            # Only transfer if A and C are friends
                            cur.execute("SELECT 1 FROM friends WHERE friend1 = %s AND friend2 = %s", (a, c))
                            if not cur.fetchone():
                                continue

                            # Transferable amount is the minimum of A-B and B-C
                            transfer_amount = min(ab_owes, bc_owes)

                            # Update or insert A - C
                            cur.execute("""
                                INSERT INTO friends (friend1, friend2, owes)
                                VALUES (%s, %s, %s)
                                ON DUPLICATE KEY UPDATE owes = owes + %s
                            """, (a, c, transfer_amount, transfer_amount))

                            # Reduce A - B and B - C
                            cur.execute("""
                                UPDATE friends SET owes = owes - %s
                                WHERE friend1 = %s AND friend2 = %s
                            """, (transfer_amount, a, b))
                            cur.execute("""
                                UPDATE friends SET owes = owes - %s
                                WHERE friend1 = %s AND friend2 = %s
                            """, (transfer_amount, b, c))

                            # Reflect changes in local debt_map
                            debt_map[(a, b)] -= transfer_amount
                            debt_map[(b, c)] -= transfer_amount
                            debt_map[(a, c)] = debt_map.get((a, c), 0.0) + transfer_amount

                            keys = list(debt_map.keys())
                            transferred = True
                conn.commit()
                close_resources(conn, cur)
                flash('Payment and debts logged successfully!', 'success')
            except mysql.connector.Error as err:
                conn.rollback()
                flash(str(err), 'danger')
                close_resources(conn, cur)
            return redirect(url_for('payment'))
        else:
            close_resources(conn, cur)
            return 'Method Not Allowed', 405
    else:
        flash('Database connection failed', 'danger')

if __name__ == '__main__':
    app.run(debug=True)