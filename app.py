import os, sqlite3, bcrypt
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'dev-key-2025'

USERS = {
    'admin': {'password': bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode(), 'role': 'admin', 'email': 'admin@example.com', 'phone': '13800138000', 'balance': 99999},
    'alice': {'password': bcrypt.hashpw(b'alice2025', bcrypt.gensalt()).decode(), 'role': 'user', 'email': 'alice@example.com', 'phone': '13900139001', 'balance': 100}
}

def init_db():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, email TEXT, phone TEXT)")
    for u in [('admin','admin123','admin@example.com','13800138000'),('alice','alice2025','alice@example.com','13900139001')]:
        c.execute("INSERT OR IGNORE INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)", u)
    conn.commit()
    conn.close()

def get_user_from_sqlite(username):
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    c.execute("SELECT id, username, password, email, phone FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row

@app.route('/')
def index():
    user_info = None
    keyword = request.args.get('keyword', '')
    search_results = None
    if 'username' in session:
        user = USERS.get(session['username'])
        if user:
            user_info = {k: v for k, v in user.items() if k != 'password'}
        else:
            row = get_user_from_sqlite(session['username'])
            if row:
                user_info = {'username': row[1], 'email': row[3], 'phone': row[4], 'balance': 0, 'role': 'user'}
    if keyword:
        conn = sqlite3.connect('data/users.db')
        c = conn.cursor()
        sql = f"SELECT id, username, email, phone FROM users WHERE username LIKE '%{keyword}%' OR email LIKE '%{keyword}%'"
        print(f"[SQL] {sql}")
        c.execute(sql)
        search_results = c.fetchall()
        conn.close()
    return render_template('index.html', user_info=user_info, keyword=keyword, search_results=search_results)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = USERS.get(username)
        if user and bcrypt.checkpw(password.encode(), user['password'].encode()):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            row = get_user_from_sqlite(username)
            if row and row[2] == password:
                session['username'] = username
                return redirect(url_for('index'))
            else:
                error = '用户名或密码错误！'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        conn = sqlite3.connect('data/users.db')
        c = conn.cursor()
        sql = f"INSERT INTO users (username, password, email, phone) VALUES ('{username}', '{password}', '{email}', '{phone}')"
        print(f"[SQL] {sql}")
        c.execute(sql)
        conn.commit()
        conn.close()
        message = '注册成功，请登录'
    return render_template('register.html', message=message)

@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    sql = f"SELECT id, username, email, phone FROM users WHERE username LIKE '%{keyword}%' OR email LIKE '%{keyword}%'"
    print(f"[SQL] {sql}")
    c.execute(sql)
    results = c.fetchall()
    conn.close()
    user = None
    if 'username' in session:
        u = USERS.get(session['username'])
        if u:
            user = {k: v for k, v in u.items() if k != 'password'}
        else:
            row = get_user_from_sqlite(session['username'])
            if row:
                user = {'username': row[1], 'email': row[3], 'phone': row[4], 'balance': 0, 'role': 'user'}
    return render_template('index.html', user_info=user, keyword=keyword, search_results=results)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
