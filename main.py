#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from flask import Flask
from flask_cors import CORS
from api.conf.routes import generate_routes
from api.database.database import MySQLDBSession, db
from api.db_initializer.db_initializer import (create_admin_user,
                                               create_super_admin,
                                               create_test_user)

def create_app():
    if os.path.exists(os.path.join('api','conf','config.py')):
        from api.conf.config import SQLALCHEMY_DATABASE_URI
    else:
        from api.conf.heroku_env import SQLALCHEMY_DATABASE_URI


    sql_session = MySQLDBSession()
    # Create a flask app.
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    # CORS(app, resources={r"/.*": {"origins": ["http://127.0.0.1","http://www.example.com"]}}) 
    # Set debug true for catching the errors.
    app.config['DEBUG'] = True

    # Set database url.
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

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
        create_admin_user(db)

        # Create default test user in database.
        create_test_user(db=db)

    # Return app.
    return app


if __name__ == '__main__':

    # Create app.
    app = create_app()

    # Run app. For production use another web server.
    # Set debug and use_reloader parameters as False.
    app.run(port=5000, debug=True, host='localhost', use_reloader=True)
