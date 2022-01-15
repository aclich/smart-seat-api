#!/usr/bin/python
# -*- coding: utf-8 -*-

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
import json


class ApiUserManagement(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.sql_session = current_app.sql_session

    
    @login_check
    @role_required.permission(1)
    def get(self):
        '''get user list'''
        user_q: [User] = self.sql_session.query(User).all()
        user_list = [query_to_dict(q) for q in user_q]
        
        return {'message': 'success', 'status': 'ok', 'data': user_list}

    @login_check
    @role_required.permission(2)
    def post(self):
        user_list = request.json.get('data')
        update_count = 0
        for user in user_list:
            update_res = self.sql_session.query(User) \
                             .filter(User.id == user['id'], User.user_role != user['user_role']) \
                             .update({User.user_role: user['user_role']})
            update_count += update_res
        return {'message': 'success', 'status': 'ok', 'data': update_count}, 200