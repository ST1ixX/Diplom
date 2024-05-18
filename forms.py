from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[Email(message='Введите корректный email адрес.')])
    id_zachet = IntegerField('Номер зачетной книжки', validators=[DataRequired(), NumberRange(min=100000, max=999999, message='Номер зачетной книжки должен быть в диапазоне от 100000 до 999999.')])
    pin_code = IntegerField('Защитный пинкод', validators=[DataRequired(), NumberRange(min=1000, max=9999, message='Пинкод должен быть от 1000 до 9999.')])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, max=25, message='Пароль должен быть длиной от 6 до 25 символов.')])
    repeat_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать.')])
    submit = SubmitField('Зарегистрироваться')



