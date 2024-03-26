# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import enum
from flask_login import UserMixin
from apps import db, login_manager
from apps.authentication.util import hash_pass
from sqlalchemy.orm import relationship
from sqlalchemy import event

class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None


class Role(enum.Enum):
    ADMIN = 1
    USER = 2

    def __str__(self):
        return str(self.value)
    
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Enum(Role), default=Role.USER)
    full_name = db.Column(db.String(255), name="full_name", nullable=True)
    address = db.Column(db.String(255), name="address", nullable=True)
    city = db.Column(db.String(255), name="city", nullable=True)
    country = db.Column(db.String(255), name="country", nullable=True)
    zip = db.Column(db.String(255), name="zip", nullable=True)
    phone = db.Column(db.String(255), name="phone", nullable=True)
    avatar = db.Column(db.String(1000), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id', ondelete='cascade'), nullable=False)
    user = relationship("Users", backref="profile")

    @classmethod
    def find_by_id(cls, _id: int) -> "Profile":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_user_id(cls, _id: int):
        return cls.query.filter_by(user_id=_id).first()


# create profile
def create_profile_for_user(mapper, connection, user):
    connection.execute(Profile.__table__.insert().values(
        user_id=user.id,
    ))

event.listen(Users, 'after_insert', create_profile_for_user)