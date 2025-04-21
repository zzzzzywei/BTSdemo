from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'data.json'

# ▶ 加载或初始化数据
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_name = request.form.get('new_name', '').strip()
        if new_name and new_name not in data:
            data[new_name] = []
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        return redirect(url_for('index'))

    names = list(data.keys())
    return render_template('index.html', names=names)

@app.route('/user/<name>', methods=['GET', 'POST'])
def user_page(name):
    if name not in data:
        return "无效的名字", 404

    if request.method == 'POST' and 'content' in request.form:
        content = request.form['content'].strip()
        if content:
            # 创建带时间戳的记录
            record = {
                "content": content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            data[name].append(record)
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        return redirect(url_for('user_page', name=name))

    history = data.get(name, [])
    return render_template('user.html', name=name, history=history)

@app.route('/user/<name>/delete/<int:idx>', methods=['POST'])
def delete_entry(name, idx):
    if name in data and 0 <= idx < len(data[name]):
        data[name].pop(idx)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return redirect(url_for('user_page', name=name))

if __name__ == '__main__':
    app.run(debug=True)
