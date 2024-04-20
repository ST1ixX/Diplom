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


@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/add_money', methods=['POST', 'GET'])
def add_money():
    if request.method == 'POST':
        id_users = request.form['id_users']
        amount = request.form['amount']
        return f'id_users: {id_users}, amount: {amount}'
    else:
        return render_template('add_money.html')
    

@app.route('/add_news', methods=['POST', 'GET'])
def add_news():
    if request.method == 'POST':
        title = request.form['title']
        intro_text = request.form['intro_text']
        full_text = request.form['full_text']
        
        news = News(title=title, intro_text=intro_text, full_text=full_text)

        try:
            db.session.add(news)
            db.session.commit()
            return redirect('/')
        except:
            return "Ошибка при добавлении новости"
        
    else:
        return render_template('add_news.html')
    
@app.route('/news')
def news():
    news = News.query.order_by(News.time.desc()).all()
    return render_template('news.html', news=news)


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register_user():
    if request.method == 'POST':
        email = request.form['email_reg']
        id_zachet = request.form['id_zachet_reg']
        password = request.form['password_reg']
        repeat_password = request.form['repeat_password_reg']

        existing_user = Users.query.filter_by(id_zachet=id_zachet).first()

        if existing_user:
            return 'Пользователь с таким номером зачетной книжки уже зарегистрирован'

        if password != repeat_password:
            return 'Пароли не совпадают'

        users = Users(id_zachet=id_zachet, email=email, password=password)

        try:
            db.session.add(users)
            db.session.commit()
            return redirect('/')
        except:
            return "Ошибка при регистрации"

    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

