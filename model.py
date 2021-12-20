# coding: utf-8
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, String, text
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class SeatCategory(Base):
    __tablename__ = 'seat_category'

    c_id = Column(INTEGER, primary_key=True)
    type_name = Column(String(25), unique=True)


class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER, primary_key=True)
    email = Column(VARCHAR(80), nullable=False, unique=True)
    password = Column(VARCHAR(255), nullable=False)
    username = Column(VARCHAR(80), nullable=False)
    user_role = Column(Enum('user', 'admin', 'sa'), nullable=False, server_default=text("'user'"))
    created = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class SensorSeat(Base):
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
