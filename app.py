from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
import sqlite3


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    id_zachet = db.Column(db.Integer, nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Users {self.id}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_zachet = db.Column(db.Integer, db.ForeignKey('users.id_zachet'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    place = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    user = db.relationship('Users', backref=db.backref('transactions', lazy=True))

    def __repr__(self):
        return f'<Transaction {self.id}>'

class PaymentPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<PaymentPoint {self.id}>'

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    topic = db.Column(db.String(50), nullable=False)
    intro_text = db.Column(db.String(200), nullable=False)
    full_text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<News {self.id}>'


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/upload-video', methods=['POST'])
def upload_video():
    video = request.files['video']
    if video:
        filename = secure_filename(video.filename)
        video.save(os.path.join('./upload-video', filename))
        return 'Видео успешно загружено', 200
    return 'Ошибка при загрузке видео', 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

