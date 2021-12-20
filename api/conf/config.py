#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DB_NAME = 'smart_seats'
# Create a database in project and get it's path.
# SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "test.db")
SQL_HOST = 'localhost'
SQL_PORT = 3306
SQL_USER = 'root'
SQL_PASSWD = 'aiotlab208'
SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{SQL_USER}:{SQL_PASSWD}@{SQL_HOST}:{SQL_PORT}/{DB_NAME}'
