import os, uuid, sqlite3, bcrypt
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory

app = Flask(__name__)
app.secret_key = 'dev-key-2025'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        c.execute("INSERT INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)", (username, password, email, phone))
        conn.commit()
        conn.close()
        message = '注册成功，请登录'
    return render_template('register.html', message=message)

@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    conn = sqlite3.connect('data/users.db')
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
                user = {'username': row[1], 'email': row[3], 'phone': row[4], 'balance': 0, 'role': 'user'}
    return render_template('index.html', user_info=user, keyword=keyword, search_results=results)

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
