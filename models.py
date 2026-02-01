import sqlite3

def get_conn():
    return sqlite3.connect("database.db")

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        email TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS items(
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        type TEXT,
        name TEXT,
        category TEXT,
        description TEXT,
        location TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

# ---------- USERS ----------
def register_user(email, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (NULL,?,?)", (email, password))
    conn.commit()
    conn.close()

def login_user(email, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email,password))
    user = c.fetchone()
    conn.close()
    return user

# ---------- ITEMS ----------
def add_item(user_id, type_, data):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO items VALUES (NULL,?,?,?,?,?,?,?)",
        (user_id, type_, data["name"], data["category"],
         data["description"], data["location"], type_))
    conn.commit()
    conn.close()

def get_items(type_):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM items WHERE type=?", (type_,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_user_items(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM items WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def update_status(item_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE items SET status='recovered' WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
