from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'dev-key-2025'

USERS = {
    'admin': {'password': 'admin123', 'role': 'admin', 'email': 'admin@example.com', 'phone': '13800138000', 'balance': 99999},
    'alice': {'password': 'alice2025', 'role': 'user', 'email': 'alice@example.com', 'phone': '13900139001', 'balance': 100}
}

@app.route('/')
def index():
    user_info = None
    if 'username' in session:
        user = USERS.get(session['username'])
        if user:
            user_info = user
    return render_template('index.html', user_info=user_info)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = USERS.get(username)
        if user and user['password'] == password:
            session['username'] = username
            return render_template('index.html', user_info=user)
        else:
            error = '用户名或密码错误！'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
