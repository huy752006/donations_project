from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///donations.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Khóa bảo mật cho session
db = SQLAlchemy(app)

# Thông tin đăng nhập admin
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'

# Model lưu trữ giao dịch
class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    message = db.Column(db.String(200), nullable=True)

# Tạo database
with app.app_context():
    db.create_all()

# Trang chủ hiển thị danh sách giao dịch
@app.route('/')
def index():
    donations = Donation.query.all()
    is_admin = session.get('admin', False)
    return render_template('index.html', donations=donations, is_admin=is_admin)

# Trang đăng nhập admin
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('index'))
    return render_template('login.html')

# Đăng xuất admin
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

# Thêm giao dịch mới (chỉ admin)
@app.route('/add', methods=['POST'])
def add_donation():
    if not session.get('admin'):
        return redirect(url_for('index'))
    
    name = request.form['name']
    amount = request.form['amount']
    message = request.form['message']
    
    new_donation = Donation(name=name, amount=float(amount), message=message)
    db.session.add(new_donation)
    db.session.commit()
    
    return redirect(url_for('index'))

# Xóa giao dịch (chỉ admin)
@app.route('/delete/<int:id>', methods=['POST'])
def delete_donation(id):
    if not session.get('admin'):
        return redirect(url_for('index'))
    
    donation = Donation.query.get(id)
    if donation:
        db.session.delete(donation)
        db.session.commit()
    return redirect(url_for('index'))

# Nhập giao dịch từ CSV (chỉ admin)
@app.route('/import', methods=['POST'])
def import_csv():
    if not session.get('admin'):
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file and file.filename.endswith('.csv'):
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            donation = Donation(name=row['name'], amount=row['amount'], message=row.get('message', ''))
            db.session.add(donation)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
