from datetime import datetime
import yookassa
from yookassa import Configuration, Payment
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify, abort, flash
from flask_sqlalchemy import SQLAlchemy
import os
import traceback
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
from functools import wraps
import uuid
from forms import RegisterForm


load_dotenv()
s = URLSafeTimedSerializer('6fff877cdac3cef7ecd27e28f2630fb26df851dd35fdcc05913efd1003b2179a')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.secret_key = 'your_secret_key_here'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
app.config['MAIL_SERVER'] = 'smtp.yandex.ru'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apppay2024@yandex.ru'
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)
Configuration.account_id = os.getenv('accountId')
Configuration.secret_key = os.getenv('secret_key')


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_zachet = db.Column(db.Integer, nullable=False, unique=True)
    pin_code = db.Column(db.String(128), default='0')
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  
    balance = db.Column(db.Integer, default=0)
    confirmed = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_store = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Users {self.id}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    payment_point_id = db.Column(db.Integer, db.ForeignKey('payment_point.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=True)  

    user = db.relationship('Users', backref=db.backref('transactions', lazy='select'))
    payment_point = db.relationship('PaymentPoint', backref=db.backref('transactions', lazy='select'))

    def __repr__(self):
        return f'<Transaction {self.id}>'


class PaymentPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id_zachet'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float) 
    longitude = db.Column(db.Float)  

    owner = db.relationship('Users', backref=db.backref('payment_points', lazy='select'))

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

class TemporaryUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_zachet = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    pin_code = db.Column(db.Integer, default=0)
    token = db.Column(db.String(128), unique=True, nullable=False)  

    def __repr__(self):
        return f'<TemporaryUser {self.email}>'


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  
        return f(*args, **kwargs)
    return decorated_function


def store_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_store:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('news'))


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


def send_confirmation(email, token):
    confirm_url = url_for('confirm_email', token=token, _external=True)
    msg = Message('Подтверждение учетной записи', sender='apppay2024@yandex.ru', recipients=[email])
    msg.body = f'Для подтверждения учетной записи и завершения регистрации перейдите по ссылке: {confirm_url}'
    mail.send(msg)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    store_points = None
    if current_user.is_store:
        store_points = current_user.payment_points  
    return render_template('profile.html', store_points=store_points)


@app.route('/transactions')
@login_required
def transactions():
    query = Transaction.query.filter_by(user_id=current_user.id_zachet)
    search_term = request.args.get('search')
    sort_by = request.args.get('sort_by')

    if search_term:
        query = query.filter(Transaction.user_id.contains(search_term) | Transaction.amount.contains(search_term))
    
    if sort_by == 'date_desc':
        query = query.order_by(Transaction.date.desc())
    elif sort_by == 'date_asc':
        query = query.order_by(Transaction.date.asc())
    elif sort_by == 'amount_desc':
        query = query.order_by(Transaction.amount.desc())
    elif sort_by == 'amount_asc':
        query = query.order_by(Transaction.amount.asc())

    transactions = query.all()
    return render_template('transactions.html', transactions=transactions)


@app.route('/all_transactions')
@store_required
def all_transactions():
    query = Transaction.query \
        .join(PaymentPoint, Transaction.payment_point_id == PaymentPoint.id) \
        .filter(PaymentPoint.owner_id == current_user.id_zachet)
    
    search_term = request.args.get('search')
    sort_by = request.args.get('sort_by')

    if search_term:
        query = query.filter(Transaction.user_id.contains(search_term) | Transaction.amount.contains(search_term))
    
    if sort_by == 'date_desc':
        query = query.order_by(Transaction.date.desc())
    elif sort_by == 'date_asc':
        query = query.order_by(Transaction.date.asc())
    elif sort_by == 'amount_desc':
        query = query.order_by(Transaction.amount.desc())
    elif sort_by == 'amount_asc':
        query = query.order_by(Transaction.amount.asc())

    transactions = query.all()
    return render_template('all_transactions.html', transactions=transactions)


@app.route('/all_user_transactions')
@admin_required
def all_user_transactions():
    query = Transaction.query \
        .join(PaymentPoint, Transaction.payment_point_id == PaymentPoint.id)
    
    search_term = request.args.get('search')
    sort_by = request.args.get('sort_by')

    if search_term:
        query = query.filter(Transaction.user_id.contains(search_term) | Transaction.amount.contains(search_term))
    
    if sort_by == 'date_desc':
        query = query.order_by(Transaction.date.desc())
    elif sort_by == 'date_asc':
        query = query.order_by(Transaction.date.asc())
    elif sort_by == 'amount_desc':
        query = query.order_by(Transaction.amount.desc())
    elif sort_by == 'amount_asc':
        query = query.order_by(Transaction.amount.asc())

    transactions = query.all()
    return render_template('all_user_transactions.html', transactions=transactions)


@app.route('/news')
def news():
    news = News.query.order_by(News.time.desc()).all()
    return render_template('news.html', news=news)


@app.route('/add_money', methods=['POST', 'GET'])
@admin_required
def add_money():
    if request.method == 'POST':
        id_users = request.form['id_users']
        amount = request.form['amount']
        
        try:
            user = Users.query.filter_by(id_zachet=id_users).first()
            if user:

                user.balance += int(amount)
                db.session.commit()
                return redirect('/profile')
            else:
                return "Пользователь не найден"
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            return f"Ошибка при добавлении денег: {str(e)}"
        
    else:
        return render_template('add_money.html')


@app.route('/add_news', methods=['POST', 'GET'])
@admin_required
def add_news():
    if request.method == 'POST':
        title = request.form['title']
        intro_text = request.form['intro_text']
        full_text = request.form['full_text']
        
        news = News(title=title, intro_text=intro_text, full_text=full_text)

        try:
            db.session.add(news)
            db.session.commit()
            db.session.close()
            return redirect('/')
        except:
            return "Ошибка при добавлении новости"
        
    else:
        return render_template('add_news.html')
    

@app.route('/news/<int:news_id>/delete')
@admin_required
def delete_news(news_id):
    news = News.query.get(news_id)
    db.session.delete(news)
    db.session.commit()
    return redirect('/news')
    

@app.route('/news/<int:news_id>')
def news_detail(news_id):
    news = News.query.get(news_id)
    return render_template('news_detail.html', news=news)



@app.route('/ballance')
@login_required
def ballance():
    return render_template('ballance.html')


@app.route('/add_ballance', methods=['POST', 'GET'])
@login_required
def add_ballance():
    if request.method == 'POST':
        amount = request.form['money']
        pin_code = request.form['pincode']

        user = Users.query.filter_by(id_zachet=current_user.id_zachet).first()
        if user and check_password_hash(user.pin_code, pin_code):
            user.balance += int(amount)
            db.session.commit()
            
            payment = Payment.create({
                "amount": {
                    "value": str(amount),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": "http://127.0.0.1:5000/profile"
                },
                "capture": True,
                "description": f"Оплата от пользователя {user.id_zachet}",
                "metadata": {
                    "user_id": user.id_zachet
                }
            })
            return redirect(payment.confirmation.confirmation_url)
        else:
            flash('Произошла ошибка', 'error')
        
    return redirect(url_for('profile'))


@app.route('/set_pincode', methods=['POST', 'GET'])
@login_required
def set_pincode():
    if request.method == 'POST':
        pin_code = request.form['pin_code']
        password = request.form['password'] 
        user = Users.query.filter_by(id_zachet=current_user.id_zachet).first()
        if user and check_password_hash(user.password, password):

            hashed_pin_code = generate_password_hash(pin_code)
            try:
                user.pin_code = hashed_pin_code
                db.session.commit()
                flash("Пин-код успешно изменён.", 'success')  # Flash сообщение об успехе
                return redirect(url_for('profile'))
            except Exception as e:
                traceback.print_exc()
                flash(f"Ошибка при установке пинкода: {str(e)}", 'error')
                return redirect(url_for('profile'))
        else:
            flash("Ошибка при установке пинкода", 'error')
            return redirect(url_for('profile'))


@app.route('/register', methods=['POST', 'GET'])
def register_user():
    if request.method == 'POST':
        email = request.form['email_reg']
        id_zachet = request.form['id_zachet_reg']
        password = request.form['password_reg']
        repeat_password = request.form['repeat_password_reg']
        pin_code = request.form['pin_code']

        if password != repeat_password:
            flash('Пароли не совпадают', 'warning')
            return redirect(url_for('register_user'))

        if TemporaryUser.query.filter((TemporaryUser.email == email) | (TemporaryUser.id_zachet == id_zachet)).first():
            flash('Пользователь с таким email или номером уже в процессе регистрации', 'error')
            return redirect(url_for('register_user'))

        hashed_password = generate_password_hash(password)
        hashed_pin_code = generate_password_hash(pin_code)
        token = s.dumps(email, salt='email-confirm')
        new_temp_user = TemporaryUser(id_zachet=id_zachet, email=email, password=hashed_password, pin_code=hashed_pin_code, token=token)
        db.session.add(new_temp_user)
        db.session.commit()

        send_confirmation(email, token)
        flash("Подтвердите учетную запись, перейдя по ссылке, отправленной вам на почту", 'warning')
        return render_template('index.html')
    else:
        return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        login_input = request.form['id_zachet_login']
        password = request.form['password_login']

        user = None
        if '@' in login_input:
            user = Users.query.filter_by(email=login_input).first()
        else:
            user = Users.query.filter_by(id_zachet=login_input).first()

        if user and check_password_hash(user.password, password):
            if not user.confirmed:
                return 'Пожалуйста, подтвердите свой email'
            remember_me = True if request.form.get('remember-me') else False
            login_user(user, remember=remember_me)
            return redirect('/')
        else:
            return 'Неверный номер зачетной книжки или пароль'
    return render_template('profile.html')


@app.route('/confirm_email/<token>')
def confirm_email(token):
    temp_user = TemporaryUser.query.filter_by(token=token).first()
    if not temp_user:
        return 'Ошибка: неверный токен или пользователь уже подтвержден.', 404

    new_user = Users(id_zachet=temp_user.id_zachet, email=temp_user.email, password=temp_user.password, pin_code=temp_user.pin_code, confirmed=True)
    db.session.add(new_user)
    db.session.delete(temp_user)
    db.session.commit()
    return 'Ваш email подтвержден!', 200


@app.route('/create-folder', methods=['POST'])
def create_folder():
    folder_name = request.args.get('folderName')
    os.makedirs(folder_name, exist_ok=True)
    return 'Folder created', 200


@app.route('/save-snapshot', methods=['POST'])
def save_snapshot():
    folder_name = request.args.get('folderName')
    snapshot = request.files['snapshot']
    if snapshot:
        filename = secure_filename(snapshot.filename)
        snapshot.save(os.path.join(folder_name, filename))
        return 'Snapshot saved', 200
    return 'Error saving snapshot', 400


@app.route('/face-login', methods = ['GET', 'POST'])
@store_required
def face_login():
    return render_template('face_login.html')


@app.route('/models/<path:filename>')
def models(filename):
    return send_from_directory('models', filename)

@app.route('/snapshots/<path:filename>')
def serve_snapshots(filename):
    return send_from_directory('snapshots', filename)


@app.route('/get-user-ids')
def get_user_ids():
    directory = 'snapshots'
    user_ids = [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]
    return jsonify(user_ids)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email_forgot'] 
        user = Users.query.filter_by(email=email).first()
        if user:
            token = s.dumps(email, salt='recover-password')
            recover_url = url_for('reset_password', token=token, _external=True)
            msg = Message('Восстановление пароля', sender='apppay2024@yandex.ru', recipients=[email])
            msg.body = f'Для сброса пароля перейдите по ссылке: {recover_url}'
            mail.send(msg)
            flash('Инструкции по восстановлению пароля отправлены на вашу почту.', 'info')
            return redirect(url_for('forgot_password'))
        else:
            flash('Пользователь с таким email не найден.', 'error')
    return render_template('forgot_password.html')


@app.route('/add_payment', methods=['POST', 'GET'])
@store_required  
def add_payment():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        
        payment = PaymentPoint(name=name, location=location, owner_id=current_user.id_zachet)

        try:
            db.session.add(payment)
            db.session.commit()
            flash("Новый пункт платежа успешно добавлен.", 'success')
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при добавлении магазина: {str(e)}", 'error')
            return render_template('add_payment.html')
    else:
        return render_template('add_payment.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='recover-password', max_age=3600)
    except SignatureExpired:
        return 'Ссылка для восстановления пароля истекла.', 400
    except:
        return 'Неверный токен.', 400

    if request.method == 'POST':
        new_password = request.form['password']
        user = Users.query.filter_by(email=email).first()
        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash('Ваш пароль был успешно обновлён.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html')


@app.route('/pay', methods=['POST', 'GET'])
@store_required
def pay():
    if request.method == 'POST':
        amount = request.form['amount_pay']
        pin_code = request.form['pin_code']
        user_id = request.form['user_id']

        if current_user.is_store:
            payment_point = PaymentPoint.query.filter_by(owner_id=current_user.id_zachet).first()
            if not payment_point:
                flash('У вашего магазина нет зарегистрированных точек оплаты.', 'error')
                return redirect(url_for('profile'))

            payment_point_id = payment_point.id

        user = Users.query.filter_by(id_zachet=user_id).first()
        store_owner = Users.query.filter_by(id_zachet=payment_point.owner_id).first()
        if check_password_hash(user.pin_code, pin_code)  and user.balance >= int(amount):
            user.balance -= int(amount)
            store_owner.balance += int(amount)

            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                payment_point_id=payment_point_id
            )

            db.session.add(transaction)
            db.session.commit()
            flash('Оплата прошла успешно', 'success')
            return redirect(url_for('face_login'))
        else:
            flash('Недостаточно средств или неверный пин-код', 'error')

    return redirect(url_for('face_login'))


@app.route('/hand_pay')
@store_required
def hand_pay():
    return render_template('hand_pay.html')


@app.route('/pay_amount', methods=['POST', 'GET'])
@store_required
def pay_amount():
    if request.method == 'POST':
        amount = request.form['amount_pay']
        pin_code = request.form['pin_code']
        user_id = request.form['user_id']

        if current_user.is_store:
            payment_point = PaymentPoint.query.filter_by(owner_id=current_user.id_zachet).first()
            if not payment_point:
                flash('У вашего магазина нет зарегистрированных точек оплаты.', 'error')
                return redirect(url_for('profile'))

            payment_point_id = payment_point.id

        user = Users.query.filter_by(id_zachet=user_id).first()
        store_owner = Users.query.filter_by(id_zachet=payment_point.owner_id).first()
        if check_password_hash(user.pin_code, pin_code)  and user.balance >= int(amount):

            user.balance -= int(amount)
            store_owner.balance += int(amount)

            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                payment_point_id=payment_point_id
            )

            db.session.add(transaction)
            db.session.commit()
            flash('Оплата прошла успешно', 'success')
            return redirect(url_for('face_login'))
        else:
            flash('Недостаточно средств или неверный пин-код', 'error')

    return redirect(url_for('face_login'))


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    payment_id = data['object']['id']
    payment = Payment.find(payment_id)
    transaction = Transaction.query.filter_by(id=payment.metadata['transaction_id']).first()

    if payment.status == 'succeeded':
        transaction.status = 'succeeded' 
    elif payment.status == 'cancelled':
        transaction.status = 'cancelled'

    db.session.commit()
    return 'Webhook received', 200


@app.route('/upload-video', methods=['POST'])
def upload_video():
    video = request.files['video']
    if video:
        filename = secure_filename(video.filename)
        video.save(os.path.join('./upload-video', filename))
        return 'Видео успешно загружено', 200
    return 'Ошибка при загрузке видео', 400


@app.route('/regist', methods=['GET', 'POST'])
def regist():
    form = RegisterForm()
    if form.validate_on_submit():
        # Здесь можно добавить логику создания пользователя и сохранения его в базу данных
        flash('Вы успешно зарегистрировались!', 'success')
        return redirect(url_for('login'))  # Перенаправление на страницу входа после регистрации
    return render_template('reg.html', form=form)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

    

