import sqlite3
from datetime import datetime
import os

DATABASE = 'lostandfound.db'

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create lost_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lost_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            item_name TEXT NOT NULL,
            description TEXT NOT NULL,
            color TEXT,
            location TEXT NOT NULL,
            lost_date TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            contact_phone TEXT NOT NULL,
            contact_email TEXT,
            photo_path TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create found_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS found_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            item_name TEXT NOT NULL,
            description TEXT NOT NULL,
            color TEXT,
            found_location TEXT NOT NULL,
            found_date TEXT NOT NULL,
            current_location TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            contact_phone TEXT NOT NULL,
            photo_path TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create matches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lost_item_id INTEGER NOT NULL,
            found_item_id INTEGER NOT NULL,
            confidence_score REAL NOT NULL,
            category_score REAL,
            location_score REAL,
            description_score REAL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lost_item_id) REFERENCES lost_items (id),
            FOREIGN KEY (found_item_id) REFERENCES found_items (id)
        )
    ''')
    
    # Create verifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            claimer_otp TEXT NOT NULL,
            finder_otp TEXT NOT NULL,
            claimer_verified BOOLEAN DEFAULT 0,
            finder_verified BOOLEAN DEFAULT 0,
            verified_at TIMESTAMP,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (match_id) REFERENCES matches (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# Lost Items Operations
def insert_lost_item(category, item_name, description, color, location, lost_date, 
                     contact_name, contact_phone, contact_email, photo_path):
    """Insert a new lost item"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO lost_items (category, item_name, description, color, location, lost_date,
                               contact_name, contact_phone, contact_email, photo_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (category, item_name, description, color, location, lost_date,
          contact_name, contact_phone, contact_email, photo_path))
    
    lost_item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return lost_item_id

def get_lost_item(item_id):
    """Get a specific lost item"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM lost_items WHERE id = ?', (item_id,))
    item = cursor.fetchone()
    conn.close()
    
    return dict(item) if item else None

def get_all_lost_items():
    """Get all active lost items"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM lost_items WHERE status = "active" ORDER BY created_at DESC')
    items = cursor.fetchall()
    conn.close()
    
    return [dict(item) for item in items]

def get_recent_lost_items(limit=10):
    """Get recent lost items"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM lost_items ORDER BY created_at DESC LIMIT ?', (limit,))
    items = cursor.fetchall()
    conn.close()
    
    return [dict(item) for item in items]

# Found Items Operations
def insert_found_item(category, item_name, description, color, found_location, found_date,
                      current_location, contact_name, contact_phone, photo_path):
    """Insert a new found item"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO found_items (category, item_name, description, color, found_location, 
                                found_date, current_location, contact_name, contact_phone, photo_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (category, item_name, description, color, found_location, found_date,
          current_location, contact_name, contact_phone, photo_path))
    
    found_item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return found_item_id

def get_found_item(item_id):
    """Get a specific found item"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM found_items WHERE id = ?', (item_id,))
    item = cursor.fetchone()
    conn.close()
    
    return dict(item) if item else None

def get_all_found_items():
    """Get all active found items"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM found_items WHERE status = "active" ORDER BY created_at DESC')
    items = cursor.fetchall()
    conn.close()
    
    return [dict(item) for item in items]

def get_recent_found_items(limit=10):
    """Get recent found items"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM found_items ORDER BY created_at DESC LIMIT ?', (limit,))
    items = cursor.fetchall()
    conn.close()
    
    return [dict(item) for item in items]

# Matches Operations
def insert_match(lost_item_id, found_item_id, confidence_score, 
                category_score, location_score, description_score):
    """Insert a new match"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO matches (lost_item_id, found_item_id, confidence_score,
                           category_score, location_score, description_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (lost_item_id, found_item_id, confidence_score,
          category_score, location_score, description_score))
    
    match_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return match_id

def get_match(match_id):
    """Get a specific match with full details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.*,
               l.item_name as lost_item_name, l.description as lost_description, 
               l.category as lost_category, l.location as lost_location,
               l.contact_name as lost_contact_name, l.contact_phone as lost_contact_phone,
               f.item_name as found_item_name, f.description as found_description,
               f.category as found_category, f.found_location,
               f.contact_name as found_contact_name, f.contact_phone as found_contact_phone
        FROM matches m
        JOIN lost_items l ON m.lost_item_id = l.id
        JOIN found_items f ON m.found_item_id = f.id
        WHERE m.id = ?
    ''', (match_id,))
    
    match = cursor.fetchone()
    conn.close()
    
    return dict(match) if match else None

def get_matches_for_lost_item(lost_item_id):
    """Get all matches for a lost item"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.*, f.*,
               m.id as match_id,
               m.confidence_score, m.category_score, m.location_score, m.description_score
        FROM matches m
        JOIN found_items f ON m.found_item_id = f.id
        WHERE m.lost_item_id = ?
        ORDER BY m.confidence_score DESC
        LIMIT 3
    ''', (lost_item_id,))
    
    matches = cursor.fetchall()
    conn.close()
    
    return [dict(match) for match in matches]

def get_matches_for_found_item(found_item_id):
    """Get all matches for a found item"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.*, l.*,
               m.id as match_id,
               m.confidence_score, m.category_score, m.location_score, m.description_score
        FROM matches m
        JOIN lost_items l ON m.lost_item_id = l.id
        WHERE m.found_item_id = ?
        ORDER BY m.confidence_score DESC
        LIMIT 3
    ''', (found_item_id,))
    
    matches = cursor.fetchall()
    conn.close()
    
    return [dict(match) for match in matches]

def update_match_status(match_id, status):
    """Update match status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE matches SET status = ? WHERE id = ?', (status, match_id))
    
    conn.commit()
    conn.close()

# Verification Operations
def insert_verification(match_id, claimer_otp, finder_otp):
    """Insert a new verification record"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO verifications (match_id, claimer_otp, finder_otp)
        VALUES (?, ?, ?)
    ''', (match_id, claimer_otp, finder_otp))
    
    verification_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return verification_id

def get_verification(verification_id):
    """Get verification details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT v.*, m.lost_item_id, m.found_item_id
        FROM verifications v
        JOIN matches m ON v.match_id = m.id
        WHERE v.id = ?
    ''', (verification_id,))
    
    verification = cursor.fetchone()
    conn.close()
    
    return dict(verification) if verification else None

def update_verification(verification_id, claimer_verified=None, finder_verified=None):
    """Update verification status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if claimer_verified is not None:
        cursor.execute('UPDATE verifications SET claimer_verified = ? WHERE id = ?',
                      (claimer_verified, verification_id))
    
    if finder_verified is not None:
        cursor.execute('UPDATE verifications SET finder_verified = ? WHERE id = ?',
                      (finder_verified, verification_id))
    
    conn.commit()
    conn.close()

def mark_verification_complete(verification_id):
    """Mark verification as complete"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE verifications 
        SET status = 'completed', verified_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (verification_id,))
    
    conn.commit()
    conn.close()

# Stats and Analytics
def get_stats():
    """Get dashboard statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total lost items
    cursor.execute('SELECT COUNT(*) as count FROM lost_items')
    total_lost = cursor.fetchone()['count']
    
    # Total found items
    cursor.execute('SELECT COUNT(*) as count FROM found_items')
    total_found = cursor.fetchone()['count']
    
    # Total matches
    cursor.execute('SELECT COUNT(*) as count FROM matches')
    total_matches = cursor.fetchone()['count']
    
    # Successful recoveries
    cursor.execute('SELECT COUNT(*) as count FROM matches WHERE status = "recovered"')
    total_recovered = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        'total_lost': total_lost,
        'total_found': total_found,
        'total_matches': total_matches,
        'total_recovered': total_recovered
    }

def get_recent_recoveries(limit=5):
    """Get recent successful recoveries"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.*, l.item_name, l.category, l.created_at as lost_date
        FROM matches m
        JOIN lost_items l ON m.lost_item_id = l.id
        WHERE m.status = 'recovered'
        ORDER BY m.created_at DESC
        LIMIT ?
    ''', (limit,))
    
    recoveries = cursor.fetchall()
    conn.close()
    
    return [dict(recovery) for recovery in recoveries]

def get_timeline_events(match_id):
    """Get timeline events for a match"""
    match = get_match(match_id)
    
    if not match:
        return []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get lost item creation
    cursor.execute('SELECT created_at FROM lost_items WHERE id = ?', (match['lost_item_id'],))
    lost_created = cursor.fetchone()
    
    # Get match creation
    cursor.execute('SELECT created_at FROM matches WHERE id = ?', (match_id,))
    match_created = cursor.fetchone()
    
    # Get verification details
    cursor.execute('SELECT * FROM verifications WHERE match_id = ?', (match_id,))
    verification = cursor.fetchone()
    
    conn.close()
    
    timeline = [
        {
            'event': 'Item Reported Lost',
            'timestamp': lost_created['created_at'],
            'status': 'completed'
        },
        {
            'event': 'AI Match Found',
            'timestamp': match_created['created_at'],
            'status': 'completed',
            'details': f"{match['confidence_score']:.0f}% confidence"
        }
    ]
    
    if verification:
        timeline.append({
            'event': 'Verification Initiated',
            'timestamp': verification['created_at'],
            'status': 'completed' if verification['status'] == 'completed' else 'in_progress'
        })
        
        if verification['verified_at']:
            timeline.append({
                'event': 'Both Parties Verified',
                'timestamp': verification['verified_at'],
                'status': 'completed'
            })
    
    if match['status'] == 'recovered':
        timeline.append({
            'event': 'Item Successfully Recovered',
            'timestamp': match_created['created_at'],  # Use match timestamp as placeholder
            'status': 'completed'
        })
    
    return timeline