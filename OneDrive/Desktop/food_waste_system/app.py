from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret"


# 📦 DATABASE
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# 🔐 LOGIN PAGE
@app.route("/")
def login():
    return render_template("login.html")


# 🔑 LOGIN
@app.route("/login", methods=["POST"])
def do_login():
    user = request.form["username"]
    password = request.form["password"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (user, password)
    )

    result = cursor.fetchone()

    if result:
        session["user"] = result["username"]
        session["role"] = result["role"]
        return redirect("/dashboard")
    else:
        return "❌ Invalid Login"


# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# 📊 DASHBOARD (SHOW ALL FOOD)
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    # 🔥 SHOW ALL FOOD
    cursor.execute("SELECT * FROM food ORDER BY id DESC")
    food = cursor.fetchall()

    return render_template("dashboard.html", food=food)


# ➕ ADD FOOD (ADMIN)
@app.route("/add_food", methods=["POST"])
def add_food():
    if session.get("role") != "admin":
        return "❌ Unauthorized"

    conn = get_db()
    cursor = conn.cursor()

    data = (
        request.form["name"],
        request.form["food_type"],
        request.form["plates"],
        request.form["prep_time"],
        request.form["expiry"],
        "available",
        request.form["location"]
    )

    cursor.execute("""
        INSERT INTO food (name, food_type, plates, prep_time, expiry, status, location)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    return redirect("/dashboard")


# 🙋 REQUEST FOOD
@app.route("/request/<int:id>")
def request_food(id):
    if session.get("role") != "ngo":
        return "❌ Only NGOs can request"

    conn = get_db()
    cursor = conn.cursor()

    # 🔍 Check food
    cursor.execute("SELECT * FROM food WHERE id=?", (id,))
    food = cursor.fetchone()

    if not food:
        return "❌ Food not found"

    if food["status"] == "booked":
        return "❌ Already booked"

    # ✅ Mark as booked
    cursor.execute("UPDATE food SET status='booked' WHERE id=?", (id,))

    # 📝 Add history
    cursor.execute("""
        INSERT INTO history (food_id, ngo, time)
        VALUES (?, ?, ?)
    """, (id, session["user"], datetime.now()))

    conn.commit()

    return render_template("success.html")


# 📜 HISTORY
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT food.name, history.ngo, history.time
        FROM history
        JOIN food ON history.food_id = food.id
        ORDER BY history.id DESC
    """)

    data = cursor.fetchall()

    return render_template("history.html", data=data)


# 🔄 RESET DATA (FOR DEMO)
@app.route("/reset")
def reset():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE food SET status='available'")
    cursor.execute("DELETE FROM history")

    conn.commit()
    return redirect("/dashboard")


# ▶️ RUN APP
if __name__ == "__main__":
    app.run(debug=True)