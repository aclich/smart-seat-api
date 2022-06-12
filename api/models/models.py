#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.sql.schema import MetaData

from api.conf.token import jwt
from api.database.database import db

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, text, Enum, JSON, Integer
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata

class User(db.Model):

    # Generates default class name for table. For changing use
    # __tablename__ = 'users'

    # User id.
    id = db.Column(db.Integer, primary_key=True)

    # User name.
    username = db.Column(db.String(length=80))

    # User password.
    password = db.Column(db.String(length=80))

    # User email address.
    email = db.Column(db.String(length=80))

    # Creation time for user.
    created = db.Column(db.DateTime, default=datetime.utcnow)

    # Unless otherwise stated default role is user.
    user_role = db.Column(db.String, default="user")

    # Generates auth token.
    def generate_auth_token(self, permission_level):

        # Check if admin.
        if permission_level == 1:

            # Generate admin token with flag 1.
            token = jwt.dumps({"email": self.email, "admin": 1})

            # Return admin flag.
            return token

            # Check if admin.
        elif permission_level == 2:

            # Generate admin token with flag 1.
            token = jwt.dumps({"email": self.email, "admin": 2})

            # Return admin flag.
            return token

        # Return normal user flag.
        return jwt.dumps({"email": self.email, "admin": 0})
    
    def get_user_id(self, token):
        try:
            data = jwt.loads(token)
            return self.query.filter_by(email = data['email']).first().id
        except Exception as e:
            raise ValueError(f"Token error as {e}")

    def __repr__(self):

        # This is only for representation how you want to see user information after query.
        return "<User(id='%s', name='%s', password='%s', email='%s', created='%s')>" % (
            self.id,
            self.username,
            self.password,
            self.email,
            self.created,
        )


class Blacklist(db.Model):

    # Generates default class name for table. For changing use
    # __tablename__ = 'users'

    # Blacklist id.
    id = db.Column(db.Integer, primary_key=True)

    # Blacklist invalidated refresh tokens.
    refresh_token = db.Column(db.String(length=255))

    def __repr__(self):

        # This is only for representation how you want to see refresh tokens after query.
        return "<User(id='%s', refresh_token='%s', status='invalidated.')>" % (
            self.id,
            self.refresh_token,
        )

class SensorSeat(db.Model):
    __tablename__ = 'sensor_seats'
    __table_args__ = (
        Index('u_seat_name_id', 'seat_name', 'user_id', unique=True),
    )

    id = Column(INTEGER, primary_key=True)
    user_id = Column(ForeignKey('user.id'), nullable=False, index=True)
    seat_name = Column(String(255), nullable=False)
    seat_type = Column(ForeignKey('seat_category.c_id'), nullable=False, index=True, comment='坐墊型號')
    note = Column(String(255))
    created = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    seat_category = relationship('SeatCategory')
    user = relationship('User')

class SensorRecord(db.Model):
    __tablename__ = 'sensor_record'

    id = Column(INTEGER, primary_key=True)
    seat_id = Column(ForeignKey('sensor_seats.id'), nullable=False, index=True)
    seat_type = Column(ForeignKey('seat_category.c_id'), nullable=False, index=True)
    data = Column(String(255), nullable=False)
    sitting_posture = Column(Enum('regular', 'bias_left', 'bias_right', 'cross_left', 'cross_right', 'stand_on', '1', '2', '3', '4', '5', '6', '7', '8'))
    gender = Column(Enum('1', '2'), comment='1: Male, 2: Female')
    height = Column(Integer)
    weight = Column(Integer)
    created = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Data created time')

    seat = relationship('SensorSeat')
    seat_category = relationship('SeatCategory')

class SeatCategory(db.Model):
    __tablename__ = 'seat_category'

    c_id = Column(INTEGER, primary_key=True)
    type_name = Column(String(25), unique=True)

    @staticmethod
    def get_seat_type_name(c_id: int):
        seat_cate: SeatCategory = SeatCategory.query.filter_by(c_id=c_id).first()
        return seat_cate.type_name
    
    @staticmethod
    def get_type_map():
        '''id -> name'''
        type_map = {}
        seat_cate: [SeatCategory] = SeatCategory.query.all()
        for q in seat_cate:
            type_map[q.c_id] = q.type_name
        return type_map
    
    @staticmethod
    def get_type_map_reverse():
        '''name -> id'''
        type_map = {}
        seat_cate: [SeatCategory] = SeatCategory.query.all()
        for q in seat_cate:
            type_map[q.type_name] = q.c_id
        return type_map

def query_to_dict(query: MetaData):
    res_dict: dict = {}
    for c in query.__table__.columns:
        value = getattr(query, c.name, None)
        if isinstance(value, datetime):
            value = datetime.strftime(value, '%Y-%m-%d %H:%M:%S')
        if c.name == 'password':
            value = '******'
        res_dict.setdefault(c.name, value)
    return res_dict

def get_type_name(c_id: int):
    seat_cate: SeatCategory = SeatCategory.query.filter_by(c_id=c_id).first()
    return seat_cate.type_name
