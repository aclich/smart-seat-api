#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import session, current_app
from flask.globals import request
from api.conf.token import jwt_secret_key
from functools import wraps
from api.error.errors import NOT_LOGIN
from api.models.models import User
import jwt as py_jwt



def login_check(view_func):
    @wraps(view_func)
    def api_auth_wrapper(*args, **kwargs):
        # login checking
        if 'access_token' not in request.cookies:
            return NOT_LOGIN()
        access_token = request.cookies.get('access_token')
        try:
            access_token_de = py_jwt.decode(access_token, jwt_secret_key)
            # access_token_de = jwt.loads(access_token)    
            user: User = User.query.filter_by(email = access_token_de['email']).first()
            setattr(session, 'user_email', access_token_de['email'])
            setattr(session, 'user_id', user.id)
        except Exception as e:
            print(f'{e}')
            return NOT_LOGIN()

        return view_func(*args, **kwargs)  # 4

    return api_auth_wrapper

def json_return(code, data={}, message=''):
    if code == 0 or code == "0":
        response_success = {'message': message, 'code': 0}
        response_success["data"] = data

        return response_success
    else:
        response_error = {'message': message, 'code': code}
        return response_error
