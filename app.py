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
        # 判断是添加名字还是删除名字
        if 'new_name' in request.form:
            new_name = request.form.get('new_name', '').strip()
            if new_name and new_name not in data:
                data[new_name] = []
                save_data()
        elif 'delete_name' in request.form:
            delete_name = request.form.get('delete_name', '').strip()
            if delete_name in data:
                del data[delete_name]
                save_data()
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
            record = {
                "content": content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            data[name].append(record)
            save_data()
        return redirect(url_for('user_page', name=name))

    history = data.get(name, [])
    return render_template('user.html', name=name, history=history)

@app.route('/user/<name>/delete/<int:idx>', methods=['POST'])
def delete_entry(name, idx):
    if name in data and 0 <= idx < len(data[name]):
        data[name].pop(idx)
        save_data()
    return redirect(url_for('user_page', name=name))

def save_data():
    """统一保存数据到data.json"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    app.run(debug=True)
