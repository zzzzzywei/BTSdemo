from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# ▶︎ 数据库连接信息
DB_HOST = "你的Host"
DB_NAME = "你的Database name"
DB_USER = "你的Username"
DB_PASSWORD = "你的Password"
DB_PORT = 5432  # Render默认是5432端口

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

# ▶︎ 初始化数据库，确保表存在
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS names (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id SERIAL PRIMARY KEY,
            name_id INTEGER REFERENCES names(id) ON DELETE CASCADE,
            content TEXT,
            timestamp TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        if 'new_name' in request.form:
            new_name = request.form.get('new_name', '').strip()
            if new_name:
                try:
                    cur.execute("INSERT INTO names (name) VALUES (%s)", (new_name,))
                    conn.commit()
                except psycopg2.Error:
                    pass  # 名字重复就忽略
        elif 'delete_name' in request.form:
            delete_name = request.form.get('delete_name', '').strip()
            cur.execute("DELETE FROM names WHERE name = %s", (delete_name,))
            conn.commit()

    cur.execute("SELECT name FROM names ORDER BY name")
    names = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()

    return render_template('index.html', names=names)

@app.route('/user/<name>', methods=['GET', 'POST'])
def user_page(name):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM names WHERE name = %s", (name,))
    result = cur.fetchone()
    if not result:
        cur.close()
        conn.close()
        return "无效的名字", 404

    name_id = result[0]

    if request.method == 'POST' and 'content' in request.form:
        content = request.form['content'].strip()
        if content:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                "INSERT INTO records (name_id, content, timestamp) VALUES (%s, %s, %s)",
                (name_id, content, timestamp)
            )
            conn.commit()

        cur.close()
        conn.close()
        return redirect(url_for('user_page', name=name))

    cur.execute(
        "SELECT id, content, timestamp FROM records WHERE name_id = %s ORDER BY id",
        (name_id,)
    )
    history = [{"id": row[0], "content": row[1], "timestamp": row[2]} for row in cur.fetchall()]

    cur.close()
    conn.close()

    return render_template('user.html', name=name, history=history)

@app.route('/user/<name>/delete/<int:record_id>', methods=['POST'])
def delete_entry(name, record_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM records WHERE id = %s", (record_id,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for('user_page', name=name))

if __name__ == '__main__':
    app.run(debug=True)
