import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
INSERT INTO food (name, food_type, plates, prep_time, expiry, status)
VALUES 
('Taj Hotel', 'Veg Thali', 50, '2026-04-18 10:00', '2026-04-18 16:00', 'available'),
('Marriott', 'Non-Veg Biryani', 30, '2026-04-18 11:00', '2026-04-18 17:00', 'available'),
('Wedding Hall A', 'Mixed Buffet', 100, '2026-04-18 09:00', '2026-04-18 15:00', 'available')
""")

conn.commit()
conn.close()

print("✅ Sample food added")