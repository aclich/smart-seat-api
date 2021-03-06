#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def load_local_conf():
    with open(os.path.join(os.path.dirname(__file__),'local_conf.env'), 'r') as f:
        for line in f.read().split('\n'):
            if line.strip().startswith('#') or ':' not in line:
                continue
            key, val = line.split(':')
            if key.strip() == '' or val.strip == '':
                continue
            os.environ[key.strip()] = val.strip()

if os.path.exists(os.path.join(os.path.dirname(__file__),'local_conf.env')):
    load_local_conf()

DB_NAME = os.environ['DB_NAME']
# Create a database in project and get it's path.
# SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "test.db")
SQL_HOST = os.environ['SQL_HOST']
SQL_PORT = os.environ['SQL_PORT']
SQL_USER = os.environ['SQL_USER']
SQL_PASSWD = os.environ['SQL_PASSWD']
SQL_CONF = os.environ.get('SQL_CONF', '')
SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{SQL_USER}:{SQL_PASSWD}@{SQL_HOST}:{SQL_PORT}/{DB_NAME}{SQL_CONF}'
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS','*')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'secret')
REFRESH_SECRET_KEY = os.environ.get('REFRESH_SECRET_KEY', 'refresh-secret')