import sqlite3

def upgrade():
    try:
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        
        # Add to users
        try: c.execute("ALTER TABLE users ADD COLUMN points INTEGER DEFAULT 0")
        except: pass
        try: c.execute("ALTER TABLE users ADD COLUMN badges TEXT")
        except: pass
        try: c.execute("ALTER TABLE users ADD COLUMN phone TEXT")
        except: pass
        
        # Add to food
        try: c.execute("ALTER TABLE food ADD COLUMN is_veg INTEGER DEFAULT 1")
        except: pass
        try: c.execute("ALTER TABLE food ADD COLUMN image_path TEXT")
        except: pass
        try: c.execute("ALTER TABLE food ADD COLUMN ai_freshness_score TEXT")
        except: pass
        try: c.execute("ALTER TABLE food ADD COLUMN assigned_driver TEXT")
        except: pass
        
        # Add to history
        try: c.execute("ALTER TABLE history ADD COLUMN rating INTEGER")
        except: pass
        try: c.execute("ALTER TABLE history ADD COLUMN review TEXT")
        except: pass
        try: c.execute("ALTER TABLE history ADD COLUMN co2_saved REAL")
        except: pass

        conn.commit()
        print("V4 DB migration successful!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade()
