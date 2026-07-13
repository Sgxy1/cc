import sqlite3, os, bcrypt

def init_database():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        email TEXT,
        phone TEXT,
        balance REAL DEFAULT 0
    )""")
    users = [
        ('admin', bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode(), 'admin', 'admin@example.com', '13800138000', 99999),
        ('alice', bcrypt.hashpw(b'alice2025', bcrypt.gensalt()).decode(), 'user', 'alice@example.com', '13900139001', 100)
    ]
    c.executemany("INSERT OR IGNORE INTO users (username, password_hash, role, email, phone, balance) VALUES (?, ?, ?, ?, ?, ?)", users)
    conn.commit()
    conn.close()
    print("数据库初始化完成")

if __name__ == '__main__':
    init_database()
