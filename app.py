import os, uuid, secrets, sqlite3, bcrypt, urllib.request, urllib.error, urllib.parse, socket, subprocess, platform
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory

app = Flask(__name__)
app.secret_key = 'dev-key-2025'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
DB_PATH = os.path.join(BASE_DIR, 'data', 'users.db')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_csrf_token():
    return {'csrf_token': session.get('csrf_token', '')}

USERS = {
    'admin': {'password': bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode(), 'role': 'admin', 'email': 'admin@example.com', 'phone': '13800138000', 'balance': 99999},
    'alice': {'password': bcrypt.hashpw(b'alice2025', bcrypt.gensalt()).decode(), 'role': 'user', 'email': 'alice@example.com', 'phone': '13900139001', 'balance': 100}
}

def init_db():
    os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, email TEXT, phone TEXT, balance REAL DEFAULT 0)")
    for u in [('admin','admin123','admin@example.com','13800138000', 99999),('alice','alice2025','alice@example.com','13900139001', 100)]:
        c.execute("INSERT OR IGNORE INTO users (username, password, email, phone, balance) VALUES (?, ?, ?, ?, ?)", u)
    conn.commit()
    conn.close()

def get_user_from_sqlite(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, password, email, phone, balance FROM users WHERE username=?", (username,))
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
                user_info = {'username': row[1], 'email': row[3], 'phone': row[4], 'balance': row[5], 'role': 'user'}
    if keyword:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, username, email, phone FROM users WHERE username LIKE ? OR email LIKE ?", ('%' + keyword + '%', '%' + keyword + '%'))
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
            session['csrf_token'] = secrets.token_hex(16)
            return redirect(url_for('index'))
        else:
            row = get_user_from_sqlite(username)
            if row and row[2] == password:
                session['username'] = username
                session['csrf_token'] = secrets.token_hex(16)
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
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)", (username, password, email, phone))
        conn.commit()
        conn.close()
        message = '注册成功，请登录'
    return render_template('register.html', message=message)

@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, email, phone FROM users WHERE username LIKE ? OR email LIKE ?", ('%' + keyword + '%', '%' + keyword + '%'))
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
                user = {'username': row[1], 'email': row[3], 'phone': row[4], 'balance': row[5], 'role': 'user'}
    return render_template('index.html', user_info=user, keyword=keyword, search_results=results)

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, email, phone, balance FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        user = {'id': row[0], 'username': row[1], 'email': row[2], 'phone': row[3], 'balance': row[4]}
        return render_template('profile.html', user=user)
    return render_template('profile.html', user=None)

@app.route('/recharge', methods=['POST'])
def recharge():
    if 'username' not in session:
        return redirect(url_for('login'))
    token = request.form.get('csrf_token', '')
    if token != session.get('csrf_token', ''):
        return 'CSRF Token 无效', 400
    amount = request.form.get('amount', '')
    if not amount:
        return redirect(url_for('profile'))
    try:
        amount = float(amount)
    except ValueError:
        return redirect(url_for('profile'))
    if amount <= 0:
        return redirect(url_for('profile'))
    username = session['username']
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE username=?", (amount, username))
    conn.commit()
    conn.close()
    return redirect(url_for('profile'))

@app.route('/page')
def page():
    name = request.args.get('name', '')
    page_content = None
    if name:
        name = name.replace('..', '').replace('/', '').replace('\\', '')
        filepath = os.path.join("pages", name + ".html")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                page_content = f.read()
        else:
            page_content = "页面不存在"
    user_info = None
    if 'username' in session:
        user = USERS.get(session['username'])
        if user:
            user_info = {k: v for k, v in user.items() if k != 'password'}
        else:
            row = get_user_from_sqlite(session['username'])
            if row:
                user_info = {'username': row[1], 'email': row[3], 'phone': row[4], 'balance': row[5], 'role': 'user'}
    return render_template('index.html', user_info=user_info, keyword='', search_results=None, page_content=page_content)

@app.route('/change-password', methods=['POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))
    token = request.form.get('csrf_token', '')
    if token != session.get('csrf_token', ''):
        return 'CSRF Token 无效', 400
    old_password = request.form.get('old_password', '')
    new_password = request.form.get('new_password', '')
    username = session['username']
    user = USERS.get(username)
    if user:
        if not bcrypt.checkpw(old_password.encode(), user['password'].encode()):
            return redirect(url_for('profile'))
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        USERS[username]['password'] = hashed
    else:
        row = get_user_from_sqlite(username)
        if not row or row[2] != old_password:
            return redirect(url_for('profile'))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()
    return redirect(url_for('profile'))

@app.route('/fetch-url', methods=['POST'])
def fetch_url():
    if 'username' not in session:
        return redirect(url_for('login'))
    url = request.form.get('url', '')
    result = None
    if url:
        if not url.startswith('http://') and not url.startswith('https://'):
            result = {'status': '错误', 'content': '仅允许 http:// 和 https:// 协议'}
        else:
            try:
                host = urllib.parse.urlparse(url).hostname
                ip = socket.gethostbyname(host)
                private_prefixes = ['127.', '10.', '172.16.', '172.17.', '172.18.', '172.19.', '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.', '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.', '192.168.', '0.', '169.254.']
                is_private = False
                for prefix in private_prefixes:
                    if ip.startswith(prefix):
                        is_private = True
                        break
                if ip == '::1' or ip == 'localhost':
                    is_private = True
                if is_private:
                    result = {'status': '错误', 'content': '不允许访问内网地址'}
                else:
                    resp = urllib.request.urlopen(url, timeout=10)
                    content = resp.read().decode('utf-8', errors='ignore')[:5000]
                    result = {'status': resp.status, 'content': content}
            except Exception as e:
                result = {'status': '错误', 'content': str(e)}
    user_info = None
    if 'username' in session:
        user = USERS.get(session['username'])
        if user:
            user_info = {k: v for k, v in user.items() if k != 'password'}
        else:
            row = get_user_from_sqlite(session['username'])
            if row:
                user_info = {'username': row[1], 'email': row[3], 'phone': row[4], 'balance': row[5], 'role': 'user'}
    return render_template('index.html', user_info=user_info, keyword='', search_results=None, fetch_result=result)

@app.route('/ping', methods=['GET', 'POST'])
def ping():
    if 'username' not in session:
        return redirect(url_for('login'))
    result = None
    if request.method == 'POST':
        ip = request.form.get('ip', '')
        if ip:
            dangerous = [';', '|', '&', '$', '`', '(', ')', '{', '}', '<', '>', '\n', '\r']
            for char in dangerous:
                if char in ip:
                    result = '禁止包含危险字符: ' + char
                    break
            if result is None:
                try:
                    cmd = ['ping', '-c', '3', ip]
                    output = subprocess.check_output(cmd, timeout=30, stderr=subprocess.STDOUT)
                    result = output.decode('utf-8', errors='ignore')
                except subprocess.CalledProcessError as e:
                    result = e.output.decode('utf-8', errors='ignore')
                except Exception as e:
                    result = str(e)
    return render_template('ping.html', result=result)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))
    error = ''
    file_url = ''
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename:
            if not allowed_file(file.filename):
                error = '仅允许上传 png、jpg、jpeg、gif 格式的图片'
            else:
                ext = file.filename.rsplit('.', 1)[1].lower()
                safe_name = uuid.uuid4().hex + '.' + ext
                os.makedirs(UPLOAD_DIR, exist_ok=True)
                file.save(os.path.join(UPLOAD_DIR, safe_name))
                file_url = '/uploads/' + safe_name
        else:
            error = '请选择要上传的文件'
    return render_template('upload.html', file_url=file_url, error=error)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
