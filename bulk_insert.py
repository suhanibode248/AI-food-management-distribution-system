import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

data = [
# 📍 NAGPUR
("Radisson Blu Nagpur", "Veg Thali", 40, "2026-04-18 10:00", "2026-04-18 16:00", "available", "Wardha Road, Nagpur"),
("Le Meridien Nagpur", "Biryani", 60, "2026-04-18 11:00", "2026-04-18 17:00", "available", "Wardha Road, Nagpur"),
("Hotel Centre Point Nagpur", "Buffet", 100, "2026-04-18 09:00", "2026-04-18 15:00", "available", "Ramdaspeth, Nagpur"),

# 📍 PUNE
("JW Marriott Pune", "Snacks", 30, "2026-04-18 12:00", "2026-04-18 18:00", "available", "Senapati Bapat Road, Pune"),
("Hyatt Pune", "Lunch", 70, "2026-04-18 10:30", "2026-04-18 16:30", "available", "Kalyani Nagar, Pune"),
("The Westin Pune", "Dinner", 80, "2026-04-18 13:00", "2026-04-18 20:00", "available", "Koregaon Park, Pune"),

# 📍 HYDERABAD
("Taj Krishna Hyderabad", "Veg Meals", 50, "2026-04-18 11:00", "2026-04-18 17:00", "available", "Banjara Hills, Hyderabad"),
("ITC Kakatiya Hyderabad", "Non-Veg Meals", 45, "2026-04-18 12:00", "2026-04-18 18:00", "available", "Begumpet, Hyderabad"),
("Novotel Hyderabad", "Breakfast", 35, "2026-04-18 08:00", "2026-04-18 12:00", "available", "Hitech City, Hyderabad"),
("Hyderabad Marriott Hotel", "Dinner Buffet", 90, "2026-04-18 14:00", "2026-04-18 22:00", "available", "Tank Bund Road, Hyderabad")
]

cursor.executemany("""
INSERT INTO food (name, food_type, plates, prep_time, expiry, status, location)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", data)

conn.commit()
conn.close()

print("✅ Real Hotels Added Successfully")