import sqlite3
from datetime import datetime

DB_NAME = "sausage.db"

def init_db():
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    # Table statistic sausage
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sausage_stats (
        chat_id INTEGER,
        user_id INTEGER,
        username TEXT,
        sausage_type TEXT,
        quantity INTEGER,
        PRIMARY KEY (chat_id, user_id, sausage_type)
    )
    """)

    # Table save cooldowns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cooldowns (
        chat_id INTEGER,
        user_id INTEGER,
        last_used TEXT,
        PRIMARY KEY (chat_id, user_id)
    )
    """)

    connect.commit()
    connect.close()

def get_last_used_time(chat_id: int, user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT last_used FROM cooldowns
        WHERE chat_id = ? AND user_id = ?
    """, (chat_id, user_id))
    
    result = cursor.fetchone()
    conn.close()

    if result:
        return datetime.fromisoformat(result[0])
    return None

def update_last_used_time(chat_id: int, user_id: int, time: datetime):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cooldowns (chat_id, user_id, last_used)
        VALUES (?, ?, ?)
        ON CONFLICT(chat_id, user_id)
        DO UPDATE SET last_used = excluded.last_used
    """, (chat_id, user_id, time.isoformat()))

    conn.commit()
    conn.close()

def update_sausage_stats(chat_id: int, user_id: int, username: str, sausage: str, quantity: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sausage_stats (chat_id, user_id, username, sausage_type, quantity)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(chat_id, user_id, sausage_type)
        DO UPDATE SET quantity = quantity + excluded.quantity
    """, (chat_id, user_id, username, sausage, quantity))

    conn.commit()
    conn.close()

def get_statistics(chat_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, sausage_type, quantity
        FROM sausage_stats
        WHERE chat_id = ?
    """, (chat_id,))

    rows = cursor.fetchall()
    conn.close()

    stats = {}
    for username, sausage_type, quantity in rows:
        if username not in stats:
            stats[username] = {}
        stats[username][sausage_type] = round(quantity, 2)

    return stats
