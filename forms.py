from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange

class RegisterForm(FlaskForm):
    email_reg = StringField('Email', validators=[DataRequired(), Email()])
    id_zachet_reg = IntegerField('Номер зачетной книжки', validators=[DataRequired()])
    pin_code = IntegerField('Пинкод', validators=[DataRequired(), NumberRange(min=1000, max=9999)])
    password_reg = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    repeat_password_reg = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password_reg', message='Пароли должны совпадать')])
    submit = SubmitField('Зарегистрироваться')
