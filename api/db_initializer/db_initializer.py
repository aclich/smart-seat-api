#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

# from api.database.database import db
from api.models.models import User
from werkzeug.security import generate_password_hash
import os

def create_super_admin(db):

    # Check if admin is existed in db.
    user = User.query.filter_by(email=os.environ['sa_email']).first()

    # If user is none.
    if user is None:

        # Create admin user if it does not existed.
        user = User(
            username=os.environ["sa_username"],
            password=generate_password_hash(os.environ["sa_password"], method='sha256'),
            email=os.environ["sa_email"],
            user_role="sa",
        )

        # Add user to session.
        db.session.add(user)

        # Commit session.
        db.session.commit()

        # Print admin user status.
        logging.info("Super admin was set.")

    else:

        # Print admin user status.
        logging.info("Super admin already set.")


def create_admin_user(db):

    # Check if admin is existed in db.
    user = User.query.filter_by(email="admin_email@example.com").first()

    # If user is none.
    if user is None:

        # Create admin user if it does not existed.
        user = User(
            username="admin_username",
            password=generate_password_hash("admin_password", method='sha256'),
            email="admin_email@example.com",
            user_role="admin",
        )

        # Add user to session.
        db.session.add(user)

        # Commit session.
        db.session.commit()

        # Print admin user status.
        logging.info("Admin was set.")

    else:
        # Print admin user status.
        logging.info("Admin already set.")


def create_test_user(
    db,
    username="example_username",
    password=generate_password_hash("example_password", method='sha256'),
    email="example@example.com",
    user_role="user"
):

    # Check if admin is existed in db.
    user = User.query.filter_by(email=email).first()

    # If user is none.
    if user is None:

        # Create admin user if it does not existed.
        user = User(
            username=username,
            password=password,
            email=email,
            user_role=user_role,
        )

        # Add user to session.
        db.session.add(user)

        # Commit session.
        db.session.commit()

        # Print admin user status.
        logging.info("Test user was set.")

        # Return user.
        return user

    else:

        # Print admin user status.
        logging.info("User already set.")