import sqlite3
from datetime import datetime

DB_NAME = "sausage.db"

# Initial or create DB
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
        quantity REAL,
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


# Check cooldown
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


# Update cooldown
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


def update_sausage_stats(chat_id: int, user_id: int, username: str, sausage: str, quantity: float):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Перевірка чи вже є запис
    cursor.execute("""
        SELECT quantity FROM sausage_stats
        WHERE chat_id = ? AND user_id = ? AND sausage_type = ?
    """, (chat_id, user_id, sausage))
    row = cursor.fetchone()

    if row:
        current = row[0]
        new_total = current + quantity

        if new_total <= 0:
            cursor.execute("""
                DELETE FROM sausage_stats
                WHERE chat_id = ? AND user_id = ? AND sausage_type = ?
            """, (chat_id, user_id, sausage))
        else:
            cursor.execute("""
                UPDATE sausage_stats
                SET quantity = ?, username = ?
                WHERE chat_id = ? AND user_id = ? AND sausage_type = ?
            """, (new_total, username, chat_id, user_id, sausage))
    else:
        if quantity > 0:
            cursor.execute("""
                INSERT INTO sausage_stats (chat_id, user_id, username, sausage_type, quantity)
                VALUES (?, ?, ?, ?, ?)
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

def get_top_users(chat_id: int, limit: int=10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, SUM(quantity) as total
        FROM sausage_stats
        WHERE chat_id = ?
        GROUP BY username
        ORDER BY total DESC
        LIMIT ?
    """, (chat_id, limit))

    result = cursor.fetchall()
    conn.close()

    return [(username, round(total, 2)) for username, total in result]

def get_user_sausages(chat_id: int, user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sausage_type, quantity
        FROM sausage_stats
        WHERE chat_id = ? AND user_id = ? AND quantity > 0
    """, (chat_id, user_id))

    rows = cursor.fetchall()
    conn.close()

    return rows  # список кортежів: [(“салямі”, 1.2), (“ліверна”, 0.5)]
