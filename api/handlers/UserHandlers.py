#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta

from sqlalchemy.exc import OperationalError

from flask import g, request, make_response
from flask_restful import Resource
from flask import session
from sqlalchemy.sql.expression import true
import api.error.errors as error
from api.conf.auth import login_check
from api.conf.token import auth, refresh_jwt
from api.database.database import db
from api.models.models import Blacklist, User
from api.roles import role_required
from api.schemas.schemas import UserSchema
from werkzeug.security import generate_password_hash, check_password_hash
import json


class Index(Resource):
    @staticmethod
    def get():
        return "Hello Flask Restful Example!"


class Register(Resource):
    @staticmethod
    def post():

        try:
            # Get username, password and email.
            username, password, email = (
                request.json.get("username").strip(),
                request.json.get("password").strip(),
                request.json.get("email").strip(),
            )
        except Exception as why:

            # Log input strip or etc. errors.
            logging.info("Username, password or email is wrong. " + str(why))

            # Return invalid input error.
            return error.INVALID_INPUT_422()

        # Check if any field is none.
        # if not (username and password and email):
        #     return error.INVALID_INPUT_422
        if not username:
            return error.INVALID_INPUT_422("please enter user name")
        if not email:
            return error.INVALID_INPUT_422("please enter email")
        if not password:
            return error.INVALID_INPUT_422("please enter password")

        # Get user if it is existed.
        user = User.query.filter_by(email=email).first()

        # Check if user is existed.
        if user is not None:
            return error.ALREADY_EXIST('email already registered')
        
        if len(password) < 6:
            return error.INVALID_INPUT_422('The password needs at least 6 characters')

        # Create a new user.
        user = User(username=username, password=generate_password_hash(password, "sha256"), email=email)

        # Add user to session.
        db.session.add(user)

        # Commit session.
        db.session.commit()

        # Return success if registration is completed.
        return {"status": "registration completed."}


class Login(Resource):
    @staticmethod
    def post():

        try:
            # Get user email and password.
            email, password = (
                request.json.get("email").strip(),
                request.json.get("password").strip(),
            )
        except OperationalError as e:
            return error.SERVER_ERROR_500("連線不穩定，請從新在試一次!")

        except Exception as why:

            # Log input strip or etc. errors.
            logging.info("Email or password is wrong. " + str(why))

            # Return invalid input error.
            return error.SERVER_ERROR_500(f"{why}")

        # Check if user information is none.
        if email is None or password is None:
            return error.INVALID_INPUT_422 ("Please enter Email and password")

        # Get user if it is existed.
        user: User = User.query.filter_by(email=email).first()

        # Check if user is not existed.
        if user is None:
            return error.DOES_NOT_EXIST('Email not found! Please register first!')
        
        if check_password_hash(user.password, password) is False:
            return error.INVALID_INPUT_422("Email or Password wrong!")

        if user.user_role == "user":
            # Generate access token. This method takes boolean value for checking admin or normal user. Admin: 1 or 0.
            permission = 0

        # If user is admin.
        elif user.user_role == "admin":
            # Generate access token. This method takes boolean value for checking admin or normal user. Admin: 1 or 0.
            permission = 1

        # If user is super admin.
        elif user.user_role == "sa":
            # Generate access token. This method takes boolean value for checking admin or normal user. Admin: 2, 1, 0.
            permission = 2

        else:
            return error.INVALID_INPUT_422

        access_token = user.generate_auth_token(permission)

        # Generate refresh token.
        refresh_token = refresh_jwt.dumps({"email": email})

        # Return access token and refresh token.
        data = {
            'username': user.username,
            'userrole': user.user_role,
            'permission': permission
        }

        secure = False if request.environ.get('wsgi.url_scheme', 'http') == 'http' else True
        samesite = 'None' if secure else 'Lax'
        resp = make_response(json.dumps(data))
        resp.set_cookie(key="access_token", secure=secure, samesite=samesite, value=access_token.decode(), expires=datetime.utcnow()+timedelta(hours=4, minutes=0))
        resp.set_cookie(key="refresh_token", secure=secure, samesite=samesite, value=refresh_token.decode(), expires=datetime.utcnow()+timedelta(hours=4, minutes=0))
        # resp.data = json.dumps(data)
        return resp
        # return {
        #     "access_token": access_token.decode(),
        #     "refresh_token": refresh_token.decode(),
        # }

class Logout(Resource):
    @staticmethod
    @login_check
    def post():

        # Get refresh token.
        refresh_token = request.cookies.get("refresh_token")

        # Get if the refresh token is in blacklist
        ref = Blacklist.query.filter_by(refresh_token=refresh_token).first()

        # Check refresh token is existed.
        if ref is None:
            # return {"status": "already invalidated", "refresh_token": refresh_token}

            # Create a blacklist refresh token.
            blacklist_refresh_token = Blacklist(refresh_token=refresh_token)

            # Add refresh token to session.
            db.session.add(blacklist_refresh_token)

            # Commit session.
            db.session.commit()

            # Return status of refresh token.
        secure = False if request.environ.get('wsgi.url_scheme', 'http') == 'http' else True
        samesite = 'None' if secure else 'Lax'
        resp = make_response("success")
        resp.set_cookie(key="access_token", value="", expires=datetime(1998,12,31), secure=secure, samesite=samesite)
        resp.set_cookie(key="refresh_token", value="", expires=datetime(1998,12,31), secure=secure, samesite=samesite)
        
        return resp


class RefreshToken(Resource):
    @staticmethod
    def post():

        # Get refresh token.
        refresh_token = request.json.get("refresh_token")

        # Get if the refresh token is in blacklist.
        ref = Blacklist.query.filter_by(refresh_token=refresh_token).first()

        # Check refresh token is existed.
        if ref is not None:

            # Return invalidated token.
            return {"status": "invalidated"}

        try:
            # Generate new token.
            data = refresh_jwt.loads(refresh_token)

        except Exception as why:
            # Log the error.
            logging.error(why)

            # If it does not generated return false.
            return False

        # Create user not to add db. For generating token.
        user = User(email=data["email"])

        # New token generate.
        token = user.generate_auth_token(False)

        # Return new access token.
        return {"access_token": token}


class ResetPassword(Resource):
    @auth.login_required
    def post(self):

        # Get old and new passwords.
        old_pass, new_pass = request.json.get("old_pass"), request.json.get("new_pass")

        # Get user. g.user generates email address cause we put email address to g.user in models.py.
        user = User.query.filter_by(email=g.user).first()

        # Check if user password does not match with old password.
        if user.password != old_pass:

            # Return does not match status.
            return {"status": "old password does not match."}

        # Update password.
        user.password = new_pass

        # Commit session.
        db.session.commit()

        # Return success status.
        return {"status": "password changed."}


class UsersData(Resource):
    @auth.login_required
    @role_required.permission(2)
    def get(self):
        try:

            # Get usernames.
            usernames = (
                []
                if request.args.get("usernames") is None
                else request.args.get("usernames").split(",")
            )

            # Get emails.
            emails = (
                []
                if request.args.get("emails") is None
                else request.args.get("emails").split(",")
            )

            # Get start date.
            start_date = datetime.strptime(request.args.get("start_date"), "%d.%m.%Y")

            # Get end date.
            end_date = datetime.strptime(request.args.get("end_date"), "%d.%m.%Y")

            print(usernames, emails, start_date, end_date)

            # Filter users by usernames, emails and range of date.
            users = (
                User.query.filter(User.username.in_(usernames))
                .filter(User.email.in_(emails))
                .filter(User.created.between(start_date, end_date))
                .all()
            )

            # Create user schema for serializing.
            user_schema = UserSchema(many=True)

            # Get json data
            data, errors = user_schema.dump(users)

            # Return json data from db.
            return data

        except Exception as why:

            # Log the error.
            logging.error(why)

            # Return error.
            return error.INVALID_INPUT_422


# auth.login_required: Auth is necessary for this handler.
# role_required.permission: Role required user=0, admin=1 and super admin=2.


class DataUserRequired(Resource):
    @login_check
    def get(self):
        user = User.query.filter_by(id=session.user_id).first()
        return f"Hello {user.username}, id={session.user_id} email={session.user_email} Test user data."


class DataAdminRequired(Resource):
    @auth.login_required
    @role_required.permission(1)
    def get(self):

        return "Test admin data."


class DataSuperAdminRequired(Resource):
    @auth.login_required
    @role_required.permission(2)
    def get(self):

        return "Test super admin data."
