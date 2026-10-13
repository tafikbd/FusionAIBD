import sqlite3
from datetime import datetime, timedelta

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT, plan TEXT DEFAULT 'free', premium_until TEXT, daily_count INTEGER DEFAULT 0, total_ask INTEGER DEFAULT 0, last_reset TEXT, mode TEXT DEFAULT 'fusion', refer_by INTEGER, refer_count INTEGER DEFAULT 0, banned INTEGER DEFAULT 0, joined_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS payments (payment_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, user_name TEXT, plan TEXT, duration TEXT, amount INTEGER, method TEXT, trx_id TEXT, screenshot TEXT, status TEXT DEFAULT 'pending', timestamp TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, question TEXT, answer TEXT, mode TEXT, timestamp TEXT)")
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB_PATH)

def get_user(user_id):
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(user_id, name, username="", refer_by=None):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("INSERT OR IGNORE INTO users (user_id, name, username, plan, daily_count, total_ask, last_reset, mode, refer_by, joined_at) VALUES (?, ?, ?, 'free', 0, 0, ?, 'fusion', ?, ?)", (user_id, name, username, now, refer_by, now))
    conn.commit()
    conn.close()
    if refer_by:
        update_refer_count(refer_by)

def update_user(user_id, **kwargs):
    if not kwargs:
        return
    conn = get_conn()
    c = conn.cursor()
    fields = ", ".join([k + "=?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [user_id]
    c.execute("UPDATE users SET " + fields + " WHERE user_id=?", values)
    conn.commit()
    conn.close()

def increment_ask(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET total_ask = total_ask + 1, daily_count = daily_count + 1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def reset_daily_counts():
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET daily_count=0, last_reset=?", (datetime.now().isoformat(),))
    conn.commit()
    conn.close()

def check_daily_limit(user_id, plan):
    from config import PLANS
    user = get_user(user_id)
    if not user:
        return True
    limit = PLANS.get(plan, PLANS["free"])["daily_limit"]
    return user["daily_count"] < limit

def is_premium_active(user_id):
    user = get_user(user_id)
    if not user or not user["premium_until"]:
        return False
    try:
        until = datetime.fromisoformat(user["premium_until"])
        return until > datetime.now()
    except:
        return False

def update_refer_count(referrer_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET refer_count = refer_count + 1 WHERE user_id=?", (referrer_id,))
    conn.commit()
    conn.close()

def create_payment(user_id, user_name, plan, duration, amount, method, trx_id, screenshot=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO payments (user_id, user_name, plan, duration, amount, method, trx_id, screenshot, status, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)", (user_id, user_name, plan, duration, amount, method, trx_id, screenshot, datetime.now().isoformat()))
    pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid

def get_payment(payment_id):
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM payments WHERE payment_id=?", (payment_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_pending_payments():
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM payments WHERE status='pending' ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_payment_status(payment_id, status):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE payments SET status=? WHERE payment_id=?", (status, payment_id))
    conn.commit()
    conn.close()

def activate_premium(user_id, plan, days):
    user = get_user(user_id)
    if not user:
        return
    current_until = user.get("premium_until")
    base_date = datetime.now()
    if current_until:
        try:
            existing = datetime.fromisoformat(current_until)
            if existing > base_date:
                base_date = existing
        except:
            pass
    new_until = (base_date + timedelta(days=days)).isoformat()
    update_user(user_id, plan=plan, premium_until=new_until)

def add_history(user_id, question, answer, mode):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO history (user_id, question, answer, mode, timestamp) VALUES (?, ?, ?, ?, ?)", (user_id, question[:500], answer[:2000], mode, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_history(user_id, limit=10):
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM history WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_stats():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE plan != 'free'")
    premium_users = c.fetchone()[0]
    c.execute("SELECT SUM(total_ask) FROM users")
    total_asks = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM payments WHERE status='approved'")
    approved = c.fetchone()[0]
    c.execute("SELECT SUM(amount) FROM payments WHERE status='approved'")
    revenue = c.fetchone()[0] or 0
    conn.close()
    return {"total_users": total_users, "premium_users": premium_users, "total_asks": total_asks, "approved_payments": approved, "revenue": revenue}
