# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired

# login and registration


class LoginForm(FlaskForm):
    username = StringField('Username', id='username_login', validators=[DataRequired()])
    password = PasswordField('Password', id='pwd_login', validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = StringField('Username', id='username_create', validators=[DataRequired()])
    email = StringField('Email', id='email_create', validators=[DataRequired(), Email()])
    password = PasswordField('Password', id='pwd_create', validators=[DataRequired()])


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', id='current_pwd', validators=[DataRequired()])
    new_password1 = PasswordField('New Password', id='new_pwd1', validators=[DataRequired()])
    new_password2 = PasswordField('Re-Type New Password', id='new_pwd2', validators=[DataRequired()])