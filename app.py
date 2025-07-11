from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, abort
import sqlite3
import os
import yaml
from time import time
import secrets
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

def config():
    with open('config.yml', 'r') as f:
        return yaml.safe_load(f)

def init_db():
    db = config()['database']['path']
    if not os.path.exists(db):
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS boards (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)')
        c.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                board_id INTEGER,
                name TEXT,
                option TEXT,
                message TEXT,
                file_path TEXT,
                post_time TEXT,
                parent_post_id INTEGER,
                FOREIGN KEY (board_id) REFERENCES boards(id),
                FOREIGN KEY (parent_post_id) REFERENCES posts(id)
            )
        ''')
        c.execute("INSERT INTO boards (name) VALUES ('/devel/'), ('/b/')")
        conn.commit()
        conn.close()

def allowed_ext(name):
    return '.' in name and name.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def clean_name(name):
    return os.path.splitext(secure_filename(name))[1]

@app.route('/new', methods=['POST'])
def new():
    name = request.form.get('name') or "Anonymous"
    opt = request.form.get('option')
    msg = request.form.get('message')
    board = request.form.get('board_id')
    parent = request.form.get('reply_to')
    file = request.files['file']
    stamp = int(time() * 1000)
    fname = ""

    if file and allowed_ext(file.filename):
        ext = clean_name(file.filename)
        fname = f"{stamp}{ext}"
        file.save(os.path.join(config()['database']['uploads'], fname))
    elif not parent:
        abort(403)

    conn = sqlite3.connect(config()['database']['path'])
    c = conn.cursor()

    if parent:
        c.execute('''
            INSERT INTO posts (board_id, name, option, message, file_path, post_time, parent_post_id)
            VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
        ''', (board, name, opt, msg, fname, parent))
    else:
        c.execute('''
            INSERT INTO posts (board_id, name, option, message, file_path, post_time)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        ''', (board, name, opt, msg, fname))

    conn.commit()
    conn.close()

    session['referrer'] = request.referrer
    return redirect(session.pop('referrer', url_for('new')))

def boards():
    with sqlite3.connect(config()['database']['path']) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM boards")
        return c.fetchall()

def board(name):
    with sqlite3.connect(config()['database']['path']) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM boards WHERE name=?", (f"/{name}/",))
        return c.fetchone()

def posts(name):
    with sqlite3.connect(config()['database']['path']) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT * FROM posts
            WHERE board_id = (SELECT id FROM boards WHERE name = ?)
            AND parent_post_id IS NULL
            ORDER BY post_time DESC
            LIMIT 100
        ''', (f"/{name}/",))
        return c.fetchall()

def post(pid):
    with sqlite3.connect(config()['database']['path']) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM posts WHERE id=?", (pid,))
        return c.fetchone()

def replies(pid):
    with sqlite3.connect(config()['database']['path']) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM posts WHERE parent_post_id=?", (pid,))
        return c.fetchall()

def safe_name(name):
    return all(c.isalnum() or c == '.' for c in name)

@app.route('/image/<path:name>')
def image(name):
    path = config()['database']['uploads']
    if not safe_name(name):
        abort(403)
    return send_from_directory(path, name)

@app.route('/board/<name>/')
def board_view(name):
    valid_boards = [b.strip('/') for b in config().get('boards', [])]
    if name not in valid_boards:
        abort(404)
    return render_template('board.html',
        config=config(),
        boards=boards(),
        current=board(name),
        posts=posts(name))

@app.route('/board/<name>/thread/<pid>')
def thread_view(name, pid):
    valid_boards = [b.strip('/') for b in config().get('boards', [])]
    if name not in valid_boards:
        abort(404)
    return render_template('thread.html',
        config=config(),
        boards=boards(),
        current=board(name),
        op=post(pid),
        replies=replies(pid))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
