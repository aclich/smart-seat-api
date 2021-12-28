#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from flask import Flask, current_app
from flask_cors import CORS
from api.conf.routes import generate_routes
from api.database.database import MySQLDBSession, db
from api.conf.config import SQLALCHEMY_DATABASE_URI, CORS_ALLOWED_ORIGINS
from werkzeug.middleware.proxy_fix import ProxyFix
from api.db_initializer.db_initializer import (create_admin_user,
                                               create_super_admin,
                                               create_test_user)
from api.error.errors import BaseError

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/.*": {"origins": [CORS_ALLOWED_ORIGINS]}})
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)
sql_session = MySQLDBSession()
# CORS(app, resources={r"/.*": {"origins": ["http://127.0.0.1","http://www.example.com"]}}) 
# Create a flask app.

# Set debug true for catching the errors.
app.config['DEBUG'] = True

# Set database url.
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

@app.errorhandler(Exception)
def handle_exception(e):
    current_app.logger.error((err_msg := f"{e}"), exc_info=True)
    if isinstance(e, BaseError):
        return {"message": err_msg, "code": 1}, e.http_status_code
    else:
        return {"message": err_msg, "code": 1}, 500

# Generate routes.
generate_routes(app)

# Database initialize with app.
db.init_app(app)

sql_session.init_app(app)
# Check if there is no database.
# if not os.path.exists(SQLALCHEMY_DATABASE_URI):
if True:
    # New db app if no database.
    db.app = app

    # Create all database tables.
    # db.create_all()

    # Create default super admin user in database.
    create_super_admin(db)

    # Create default admin user in database.
    # create_admin_user(db)

    # Create default test user in database.
    create_test_user(db=db)

if __name__ == '__main__':
    # Run app. For production use another web server.
    # Set debug and use_reloader parameters as False.
    app.run(port=5000, debug=True, host='0.0.0.0', use_reloader=True, ssl_context='adhoc')
