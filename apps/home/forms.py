from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField


class ProductForm(FlaskForm):
    name = StringField('Name', id='name')
    info = StringField('Info', id='info')
    price = IntegerField('Price', id='price')