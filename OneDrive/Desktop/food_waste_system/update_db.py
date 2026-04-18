import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE food ADD COLUMN location TEXT")

conn.commit()
conn.close()

print("✅ Column added successfully!")