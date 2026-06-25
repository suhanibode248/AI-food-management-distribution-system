import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import datetime
from model import predict_demand

app = Flask(__name__)
app.secret_key = 'super_secret_foodshare_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        conn = get_db_connection()
        conn.execute("""
        CREATE TABLE IF NOT EXISTS food (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            food_type TEXT,
            plates INTEGER,
            location TEXT,
            prep_time TEXT,
            expiry TEXT,
            status TEXT
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_id INTEGER,
            hotel_name TEXT,
            ngo_name TEXT,
            ngo TEXT,
            time TEXT
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT
        )
        """)
        
        # Check if users exist, otherwise insert defaults
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if users == 0:
            conn.execute("INSERT INTO users VALUES (NULL, 'admin', '1234', 'admin')")
            conn.execute("INSERT INTO users VALUES (NULL, 'ngo1', '1234', 'ngo')")
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database initialization exception (safe to ignore if locked): {e}")

init_db()

# ----------------- LIVE STATS CALCULATION -----------------
def get_dashboard_stats():
    conn = get_db_connection()
    stats = {}
    
    total_food_row = conn.execute("SELECT COUNT(id) as count FROM food").fetchone()
    stats['total_food'] = total_food_row['count'] if total_food_row else 0
    
    total_plates_row = conn.execute("SELECT SUM(plates) as total FROM food").fetchone()
    stats['total_plates'] = total_plates_row['total'] if total_plates_row and total_plates_row['total'] else 0
    
    try:
        active_ngos_row = conn.execute("SELECT COUNT(DISTINCT ngo_name) as count FROM history").fetchone()
    except sqlite3.OperationalError:
        active_ngos_row = conn.execute("SELECT COUNT(DISTINCT ngo) as count FROM history").fetchone()
    stats['active_ngos'] = active_ngos_row['count'] if active_ngos_row else 0
    
    completed_requests_row = conn.execute("SELECT COUNT(id) as count FROM history").fetchone()
    stats['completed_requests'] = completed_requests_row['count'] if completed_requests_row else 0
    
    conn.close()
    return stats

# ----------------- ROUTES -----------------

@app.route("/setup_db")
def setup_db():
    try:
        conn = get_db_connection()
        conn.execute("""
        CREATE TABLE IF NOT EXISTS food (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            food_type TEXT,
            plates INTEGER,
            location TEXT,
            prep_time TEXT,
            expiry TEXT,
            status TEXT
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_id INTEGER,
            hotel_name TEXT,
            ngo_name TEXT,
            ngo TEXT,
            time TEXT
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT
        )
        """)
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if users == 0:
            conn.execute("INSERT INTO users VALUES (NULL, 'admin', '1234', 'admin')")
            conn.execute("INSERT INTO users VALUES (NULL, 'ngo1', '1234', 'ngo')")
        conn.commit()
        conn.close()
        return "Database created successfully! You can now visit /login", 200
    except Exception as e:
        import traceback
        return f"Database creation failed: {str(e)}\n\n{traceback.format_exc()}", 500

@app.route("/")
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        role = request.form["role"]
        session["user"] = username
        session["role"] = role
        flash(f"Welcome back, {username}!", "success")
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    food_list = conn.execute("SELECT * FROM food ORDER BY id DESC").fetchall()
    conn.close()
    
    stats = get_dashboard_stats()
    
    return render_template("dashboard.html", food=food_list, stats=stats)

@app.route("/add_food", methods=["POST"])
def add_food():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))
    
    name = request.form["name"]
    food_type = request.form["food_type"]
    plates = request.form["plates"]
    location = request.form["location"]
    prep_time = request.form["prep_time"]
    expiry = request.form["expiry"]

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO food (name, food_type, plates, location, prep_time, expiry, status) VALUES (?, ?, ?, ?, ?, ?, 'available')",
        (name, food_type, plates, location, prep_time, expiry)
    )
    conn.commit()
    conn.close()
    
    flash("Food donation posted successfully! 🎉", "success")
    return redirect(url_for("dashboard"))

@app.route("/request/<int:id>")
def request_food(id):
    if session.get("role") != "ngo":
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    food = conn.execute("SELECT * FROM food WHERE id = ?", (id,)).fetchone()
    
    if food and food["status"] == "available":
        conn.execute("UPDATE food SET status = 'booked' WHERE id = ?", (id,))
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            conn.execute("INSERT INTO history (hotel_name, ngo_name, time) VALUES (?, ?, ?)", (food["name"], session["user"], time_now))
        except sqlite3.OperationalError:
            try:
                conn.execute("INSERT INTO history (hotel_name, ngo, time) VALUES (?, ?, ?)", (food["name"], session["user"], time_now))
            except sqlite3.OperationalError:
                conn.execute("INSERT INTO history (food_id, ngo, time) VALUES (?, ?, ?)", (id, session["user"], time_now))

        conn.commit()
        conn.close()
        
        flash("Request Confirmed! An SMS notification has been sent to the donor. 📩", "success")
        return redirect(url_for("dashboard"))
    
    conn.close()
    flash("Sorry, this food is no longer available.", "error")
    return redirect(url_for("dashboard"))

@app.route("/history")
def history():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    try:
        if session["role"] == "admin":
            history_data = conn.execute("SELECT hotel_name, ngo_name, time FROM history WHERE hotel_name = ? ORDER BY id DESC", (session["user"],)).fetchall()
        else:
            history_data = conn.execute("SELECT hotel_name, ngo_name, time FROM history WHERE ngo_name = ? ORDER BY id DESC", (session["user"],)).fetchall()
    except sqlite3.OperationalError:
        try:
            history_data = conn.execute("""
                SELECT food.name, history.ngo, history.time
                FROM history
                JOIN food ON history.food_id = food.id
                ORDER BY history.id DESC
            """).fetchall()
        except Exception:
            history_data = []

    conn.close()
    return render_template("history.html", data=history_data)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))

@app.route("/reset")
def reset():
    if session.get("role") == "admin":
        conn = get_db_connection()
        conn.execute("DELETE FROM food")
        conn.execute("DELETE FROM history")
        conn.commit()
        conn.close()
        flash("Database has been reset.", "success")
    return redirect(url_for("dashboard"))

# ----------------- AI API ENDPOINT -----------------
@app.route("/api/ai_recommend/<int:food_id>")
def api_ai_recommend(food_id):
    conn = get_db_connection()
    food = conn.execute("SELECT food_type, plates FROM food WHERE id = ?", (food_id,)).fetchone()
    conn.close()
    
    if not food:
        return jsonify({"error": "Food not found"}), 404
        
    recommendation = predict_demand(food['food_type'], food['plates'])
    return jsonify({"recommendation": recommendation})

if __name__ == "__main__":
    app.run(debug=True)