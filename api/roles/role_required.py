#!/usr/bin/python
# -*- coding: utf-8 -*-

import functools
import logging

from flask import request

import api.error.errors as error
from api.conf.token import jwt_secret_key
import jwt as py_jwt
# from werkzeug.datastructures import Authorization


def permission(arg):
    def check_permissions(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):

            # Check if auth is none or not.
            if 'access_token' not in request.cookies:
                return error.NOT_LOGIN

            try:
                # Get auth type and token.
                token = request.cookies['access_token']
                # auth = Authorization(auth_type, {'token': token})

                # Generate new token.
                data = py_jwt.decode(token, jwt_secret_key)

                # Check if admin
                if data["admin"] < arg:

                    # Return if user is not admin.
                    return error.NOT_ADMIN

            except ValueError:
                # The Authorization header is either empty or has no token.
                return error.HEADER_NOT_FOUND

            except Exception as why:
                # Log the error.
                logging.error(why)

                # If it does not generated return false.
                return error.INVALID_INPUT_422

                # Return method.
            return f(*args, **kwargs)

        # Return decorated method.
        return decorated

    # Return check permissions method.
    return check_permissions
