import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from model import predict_demand, analyze_food_image, chat_response

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
            status TEXT,
            requested_by TEXT,
            is_veg INTEGER DEFAULT 1,
            image_path TEXT,
            ai_freshness_score TEXT,
            assigned_driver TEXT
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_id INTEGER,
            hotel_name TEXT,
            ngo_name TEXT,
            ngo TEXT,
            time TEXT,
            rating INTEGER,
            review TEXT,
            co2_saved REAL
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT,
            phone TEXT,
            points INTEGER DEFAULT 0,
            badges TEXT
        )
        """)
        
        # Check if users exist, otherwise insert defaults
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if users == 0:
            pw = generate_password_hash('1234')
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', pw, 'admin'))
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('ngo1', pw, 'ngo'))
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('driver1', pw, 'driver'))
            
            # Seed default food data so it's not empty on Render
            from datetime import timedelta
            now = datetime.now()
            t1_prep = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
            t1_exp = (now + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M")
            t2_prep = (now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M")
            t2_exp = (now + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M")
            t3_prep = (now - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M")
            t3_exp = (now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")

            # Available food
            conn.execute(
                "INSERT INTO food (name, food_type, plates, location, prep_time, expiry, status, is_veg, ai_freshness_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("Grand Palace Hotel", "Vegetable Biryani", 50, "Downtown Avenue", t1_prep, t1_exp, "available", 1, "98% Fresh")
            )
            # Approved food (waiting for driver)
            conn.execute(
                "INSERT INTO food (name, food_type, plates, location, prep_time, expiry, status, requested_by, is_veg, ai_freshness_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("Sunrise Bakery", "Assorted Bread & Pastries", 20, "Westside Market", t2_prep, t2_exp, "approved", "ngo1", 1, "95% Fresh")
            )
            # Requested food
            conn.execute(
                "INSERT INTO food (name, food_type, plates, location, prep_time, expiry, status, requested_by, is_veg, ai_freshness_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("Ocean Catch", "Grilled Salmon", 15, "Pier 39", t3_prep, t3_exp, "requested", "ngo1", 0, "90% Fresh")
            )
            
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
    
    co2_row = conn.execute("SELECT SUM(co2_saved) as total FROM history").fetchone()
    stats['co2_saved'] = round(co2_row['total'] or 0, 1)
    
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
            status TEXT,
            requested_by TEXT,
            is_veg INTEGER DEFAULT 1,
            image_path TEXT,
            ai_freshness_score TEXT,
            assigned_driver TEXT
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_id INTEGER,
            hotel_name TEXT,
            ngo_name TEXT,
            ngo TEXT,
            time TEXT,
            rating INTEGER,
            review TEXT,
            co2_saved REAL
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT,
            phone TEXT,
            points INTEGER DEFAULT 0,
            badges TEXT
        )
        """)
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if users == 0:
            pw = generate_password_hash('1234')
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', pw, 'admin'))
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('ngo1', pw, 'ngo'))
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('driver1', pw, 'driver'))
            
            # Seed default food data so it's not empty on Render
            from datetime import timedelta
            now = datetime.now()
            t1_prep = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
            t1_exp = (now + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M")
            t2_prep = (now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M")
            t2_exp = (now + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M")
            t3_prep = (now - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M")
            t3_exp = (now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")

            conn.execute(
                "INSERT INTO food (name, food_type, plates, location, prep_time, expiry, status, is_veg, ai_freshness_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("Grand Palace Hotel", "Vegetable Biryani", 50, "Downtown Avenue", t1_prep, t1_exp, "available", 1, "98% Fresh")
            )
            conn.execute(
                "INSERT INTO food (name, food_type, plates, location, prep_time, expiry, status, requested_by, is_veg, ai_freshness_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("Sunrise Bakery", "Assorted Bread & Pastries", 20, "Westside Market", t2_prep, t2_exp, "approved", "ngo1", 1, "95% Fresh")
            )
            conn.execute(
                "INSERT INTO food (name, food_type, plates, location, prep_time, expiry, status, requested_by, is_veg, ai_freshness_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("Ocean Catch", "Grilled Salmon", 15, "Pier 39", t3_prep, t3_exp, "requested", "ngo1", 0, "90% Fresh")
            )
            
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
        password = request.form["password"]
        role = request.form["role"]
        
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND role = ?", (username, role)).fetchone()
        conn.close()
        
        if user and (check_password_hash(user['password'], password) or user['password'] == password):
            session["user"] = username
            session["role"] = role
            session["points"] = user['points']
            session["badges"] = user['badges'] or "Starter"
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials or role. Please try again.", "error")
            
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        phone = request.form["phone"]
        
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        
        if user:
            conn.close()
            flash("Username already exists.", "error")
            return redirect(url_for("register"))
            
        hashed_pw = generate_password_hash(password)
        conn.execute("INSERT INTO users (username, password, role, phone) VALUES (?, ?, ?, ?)", 
                     (username, hashed_pw, role, phone))
        conn.commit()
        conn.close()
        
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))
        
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    food_list = conn.execute("SELECT * FROM food ORDER BY id DESC").fetchall()
    
    # Refresh points in session
    user = conn.execute("SELECT points, badges FROM users WHERE username = ?", (session["user"],)).fetchone()
    if user:
        session["points"] = user["points"]
        session["badges"] = user["badges"] or "Starter"
        
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
    is_veg = request.form.get("is_veg", 1)
    
    image_path = ""
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join('static', 'uploads', filename)
            file.save(file_path)
            image_path = f"/static/uploads/{filename}"
            
    freshness = analyze_food_image(prep_time)

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO food (name, food_type, plates, location, prep_time, expiry, status, is_veg, image_path, ai_freshness_score) VALUES (?, ?, ?, ?, ?, ?, 'available', ?, ?, ?)",
        (name, food_type, plates, location, prep_time, expiry, is_veg, image_path, freshness)
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
        conn.execute("UPDATE food SET status = 'requested', requested_by = ? WHERE id = ?", (session["user"], id))
        conn.commit()
        conn.close()
        
        flash("Request sent! Waiting for donor approval. ⏳", "success")
        return redirect(url_for("dashboard"))
    
    conn.close()
    flash("Sorry, this food is no longer available.", "error")
    return redirect(url_for("dashboard"))

@app.route("/approve/<int:id>")
def approve_food(id):
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))
    
    conn = get_db_connection()
    food = conn.execute("SELECT * FROM food WHERE id = ?", (id,)).fetchone()
    
    if food and food["status"] == "requested":
        ngo_name = food["requested_by"]
        conn.execute("UPDATE food SET status = 'approved' WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        
        flash(f"Request Approved! Waiting for a driver to accept the delivery. ✅", "success")
        return redirect(url_for("dashboard"))
    
    conn.close()
    flash("Action not possible.", "error")
    return redirect(url_for("dashboard"))

@app.route("/accept_delivery/<int:id>")
def accept_delivery(id):
    if session.get("role") != "driver":
        return redirect(url_for("dashboard"))
        
    conn = get_db_connection()
    food = conn.execute("SELECT * FROM food WHERE id = ?", (id,)).fetchone()
    
    if food and food["status"] == "approved":
        conn.execute("UPDATE food SET status = 'out_for_delivery', assigned_driver = ? WHERE id = ?", (session["user"], id))
        conn.commit()
        conn.close()
        flash("Delivery accepted! Please head to the donor location. 🚚", "success")
        return redirect(url_for("dashboard"))
        
    conn.close()
    flash("Action not possible.", "error")
    return redirect(url_for("dashboard"))

@app.route("/complete_delivery/<int:id>")
def complete_delivery(id):
    if session.get("role") != "driver":
        return redirect(url_for("dashboard"))
        
    conn = get_db_connection()
    food = conn.execute("SELECT * FROM food WHERE id = ?", (id,)).fetchone()
    
    if food and food["status"] == "out_for_delivery" and food["assigned_driver"] == session["user"]:
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        co2 = float(food["plates"]) * 0.5
        
        try:
            conn.execute("INSERT INTO history (hotel_name, ngo_name, time, co2_saved) VALUES (?, ?, ?, ?)", 
                         (food["name"], food["requested_by"], time_now, co2))
        except sqlite3.OperationalError:
            conn.execute("INSERT INTO history (hotel_name, ngo, time) VALUES (?, ?, ?)", 
                         (food["name"], food["requested_by"], time_now))
                         
        conn.execute("UPDATE food SET status = 'delivered' WHERE id = ?", (id,))
        
        # Add points to driver
        conn.execute("UPDATE users SET points = points + 10 WHERE username = ?", (session["user"],))
        
        conn.commit()
        conn.close()
        flash("Delivery completed successfully! You earned 10 points! 🏆", "success")
        return redirect(url_for("dashboard"))
        
    conn.close()
    flash("Action not possible.", "error")
    return redirect(url_for("dashboard"))

@app.route("/reject/<int:id>")
def reject_food(id):
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))
    
    conn = get_db_connection()
    food = conn.execute("SELECT * FROM food WHERE id = ?", (id,)).fetchone()
    
    if food and food["status"] == "requested":
        conn.execute("UPDATE food SET status = 'available', requested_by = NULL WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        
        flash("Request Rejected. Food is back to available pool. ❌", "success")
        return redirect(url_for("dashboard"))
    
    conn.close()
    flash("Action not possible.", "error")
    return redirect(url_for("dashboard"))

@app.route("/history")
def history():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    try:
        if session["role"] == "admin":
            history_data = conn.execute("SELECT id, hotel_name, ngo_name, time, co2_saved, rating, review FROM history WHERE hotel_name = ? ORDER BY id DESC", (session["user"],)).fetchall()
        else:
            history_data = conn.execute("SELECT id, hotel_name, ngo_name, time, co2_saved, rating, review FROM history WHERE ngo_name = ? ORDER BY id DESC", (session["user"],)).fetchall()
    except sqlite3.OperationalError:
        try:
            history_data = conn.execute("""
                SELECT history.id, food.name as hotel_name, history.ngo as ngo_name, history.time, history.co2_saved, history.rating, history.review
                FROM history
                JOIN food ON history.food_id = food.id
                ORDER BY history.id DESC
            """).fetchall()
        except Exception:
            history_data = []

    conn.close()
    return render_template("history.html", data=history_data)

@app.route("/rate_history/<int:id>", methods=["POST"])
def rate_history(id):
    if session.get("role") != "ngo":
        return redirect(url_for("history"))
        
    rating = request.form.get("rating")
    review = request.form.get("review")
    
    conn = get_db_connection()
    conn.execute("UPDATE history SET rating = ?, review = ? WHERE id = ?", (rating, review, id))
    conn.execute("UPDATE users SET points = points + 5 WHERE username = ?", (session["user"],))
    conn.commit()
    conn.close()
    
    flash("Thank you for your feedback! You earned 5 points.", "success")
    return redirect(url_for("history"))

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

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json
    msg = data.get("message", "")
    reply = chat_response(msg)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)