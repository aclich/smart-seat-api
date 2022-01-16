#!/usr/bin/python
# -*- coding: utf-8 -*-

from hashlib import sha256
import logging
from datetime import datetime, timedelta
from typing import List

from flask import session, request, make_response, current_app
from flask_restful import Resource
import api.error.errors as error
from api.conf.auth import login_check
from api.models.models import SeatCategory, SensorSeat, SensorRecord, User, query_to_dict
from api.roles import role_required
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
import json


class ApiUserEdit(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.sql_session = current_app.sql_session
    
    @login_check
    def get(self):
        '''使用者編輯-取得資訊'''
        message, state, code = 'success', 'ok', 200
        user_data = {}
        try:
            user_q: User = self.sql_session.query(User).filter(User.id == session.user_id).first()
            if user_q == None:
                raise FileNotFoundError

            user_data = {'username': user_q.username, 'email': user_q.email}
        
        except FileNotFoundError:
            message = f'錯誤，查無ID={session.user_id}的使用者'
            state = 'error'
            code = 404
        
        except Exception as e:
            message = f'連線不穩定，請重新整理後在試一次!'
            state = f'error {e}'
            code = 500
        return {"message": message, "state": state, "data": user_data}, code

    @login_check
    def put(self):
        '''修改資訊'''
        req_data = request.json
        old_password = req_data.get('old_password')
        new_password = req_data.get('new_password')
        user_data = req_data.get('user_data')
        message, state, code = 'success', 'ok', 200
        try:
            user_q = self.sql_session.query(User).filter(User.id == session.user_id)
            user: User = user_q.first()
            if user_q == None:
                raise FileNotFoundError(f"錯誤，查無ID={session.user_id}的使用者")
            if check_password_hash(user.password, old_password) is False:
                raise PermissionError("密碼錯誤!")
            if new_password != '' and len(new_password) < 6:
                raise ValueError("密碼須至少6位!")
            
            update_pwd = user.password if len(new_password) == 0 else generate_password_hash(new_password, "sha256")
            
            update_res = user_q.update({User.email: user_data['email'], User.password: update_pwd, User.username: user_data['username']})
            if update_res != 1:
                raise ValueError(f"更新數={update_res}異常!")

        except IntegrityError as e:
            message = "email 已被使用過!"
            state = f"error {e}"
            code = 409
        
        except FileNotFoundError as e:
            message = f'{e}'
            state = 'error'
            code = 404
        
        except PermissionError as e:
            message = f'{e}'
            state = 'error'
            code = 409
        
        except ValueError as e:
            message = f'{e}'
            state = 'error'
            code = 409
        
        return {'message': message, 'state': state}, code