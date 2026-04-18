import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Food table
cursor.execute("""
CREATE TABLE food (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    food_type TEXT,
    plates INTEGER,
    prep_time TEXT,
    expiry TEXT,
    status TEXT
)
""")

# History table
cursor.execute("""
CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_id INTEGER,
    ngo TEXT,
    time TEXT
)
""")

# Users table
cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT
)
""")

# Default users
cursor.execute("INSERT INTO users VALUES (NULL, 'admin', '1234', 'admin')")
cursor.execute("INSERT INTO users VALUES (NULL, 'ngo1', '1234', 'ngo')")

conn.commit()
conn.close()

print("✅ Database created successfully!")