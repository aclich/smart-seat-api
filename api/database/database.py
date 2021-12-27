#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from flask_restful import Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from flask import current_app
from flask import _app_ctx_stack

from sqlalchemy import create_engine
# Create sql alchemy database object.
db = SQLAlchemy()

if os.path.exists(os.path.join('api','conf','config.py')):
    from api.conf.config import SQLALCHEMY_DATABASE_URI
else:
    from api.conf.heroku_env import SQLALCHEMY_DATABASE_URI

class MySQLDBSession(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        engine = create_engine(SQLALCHEMY_DATABASE_URI,
                               pool_size=20,
                               pool_recycle=1800,
                               pool_timeout=30,
                               encoding="utf8",
                               pool_pre_ping=True)

        sessionlocal = sessionmaker(bind=engine, autocommit=True)
        app.sql_session = scoped_session(sessionlocal, scopefunc=_app_ctx_stack.__ident_func__)