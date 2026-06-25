import sqlite3

try:
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE food ADD COLUMN requested_by TEXT")
    conn.commit()
    print("✅ Column requested_by added successfully!")
except sqlite3.OperationalError as e:
    print(f"OperationalError (possibly already exists): {e}")
finally:
    conn.close()
