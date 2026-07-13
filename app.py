import os, sqlite3, hashlib
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'dev-key-2025'

def init_db():
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
        ('admin', hashlib.md5(b'admin123').hexdigest(), 'admin', 'admin@example.com', '13800138000', 99999),
        ('alice', hashlib.md5(b'alice2025').hexdigest(), 'user', 'alice@example.com', '13900139001', 100)
    ]
    c.executemany("INSERT OR IGNORE INTO users (username, password_hash, role, email, phone, balance) VALUES (?, ?, ?, ?, ?, ?)", users)
    conn.commit()
    conn.close()

@app.route('/')
def index():
    user_info = None
    if 'username' in session:
        conn = sqlite3.connect('data/users.db')
        c = conn.cursor()
        c.execute("SELECT id, username, password_hash, role, email, phone, balance FROM users WHERE username=?", (session['username'],))
        row = c.fetchone()
        conn.close()
        if row:
            user_info = {
                'id': row[0], 'username': row[1], 'password_hash': row[2],
                'role': row[3], 'email': row[4], 'phone': row[5], 'balance': row[6]
            }
    return render_template('index.html', user_info=user_info)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hashlib.md5(password.encode()).hexdigest()
        conn = sqlite3.connect('data/users.db')
        c = conn.cursor()
        c.execute("SELECT id, username, password_hash, role, email, phone, balance FROM users WHERE username=? AND password_hash=?", (username, password_hash))
        row = c.fetchone()
        conn.close()
        if row:
            session['username'] = username
            user_info = {
                'id': row[0], 'username': row[1], 'password_hash': row[2],
                'role': row[3], 'email': row[4], 'phone': row[5], 'balance': row[6]
            }
            return render_template('index.html', user_info=user_info)
        else:
            error = '用户名或密码错误！'
    return render_template('login.html', error=error)

@app.route('/api/users')
def api_users():
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    c.execute("SELECT id, username, password_hash, role, email, phone, balance FROM users")
    rows = c.fetchall()
    conn.close()
    users = []
    for row in rows:
        users.append({
            'id': row[0], 'username': row[1], 'password_hash': row[2],
            'role': row[3], 'email': row[4], 'phone': row[5], 'balance': row[6]
        })
    return jsonify(users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
