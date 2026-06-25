import os
import sqlite3
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, init_db

init_db()

with app.test_client() as c:
    # 1. Login as admin
    c.post('/login', data={'username': 'admin', 'role': 'admin'})
    
    # 2. Add food
    c.post('/add_food', data={
        'name': 'Test Hotel',
        'food_type': 'Test Food',
        'plates': '10',
        'location': 'Test Location',
        'prep_time': '2026-06-25T12:00',
        'expiry': '2026-06-25T14:00'
    })
    
    # 3. Find the food id
    conn = sqlite3.connect('database.db')
    food_id = conn.execute("SELECT id FROM food WHERE name='Test Hotel' ORDER BY id DESC LIMIT 1").fetchone()[0]
    conn.close()
    
    # 4. Login as NGO and request
    c.post('/login', data={'username': 'ngo1', 'role': 'ngo'})
    r = c.get(f'/request/{food_id}')
    assert r.status_code == 302
    
    # 5. Check status is requested
    conn = sqlite3.connect('database.db')
    status, req_by = conn.execute("SELECT status, requested_by FROM food WHERE id=?", (food_id,)).fetchone()
    conn.close()
    assert status == 'requested'
    assert req_by == 'ngo1'
    
    # 6. Login as admin and approve
    c.post('/login', data={'username': 'admin', 'role': 'admin'})
    r = c.get(f'/approve/{food_id}')
    assert r.status_code == 302
    
    # 7. Check status is booked
    conn = sqlite3.connect('database.db')
    status = conn.execute("SELECT status FROM food WHERE id=?", (food_id,)).fetchone()[0]
    conn.close()
    assert status == 'booked'
    
    print("ALL V3 TESTS PASSED!")
