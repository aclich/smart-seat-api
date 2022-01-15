#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

from flask import request, current_app
from flask_restful import Resource
import api.error.errors as error
from api.conf.auth import login_check
from api.models.models import SeatCategory, SensorSeat, SensorRecord, User, query_to_dict
from api.roles import role_required
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy import func
import json


class ApiSeatTypeManagement(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.sql_session = current_app.sql_session

    @login_check
    @role_required.permission(1)
    def get(self):
        type_list = [query_to_dict(q) for q in self.sql_session.query(SeatCategory).order_by(SeatCategory.c_id.asc()).all()]
        return {'message': 'success', 'status': 'ok', 'data': type_list}, 200

    @login_check
    @role_required.permission(1)
    def post(self):
        '''新增型號'''
        message, state, code = 'success', 'ok', 200
        type_data = request.json
        try:
            new_c_id = self._get_c_id()
            self.sql_session.add(SeatCategory(c_id=new_c_id, type_name=type_data['type_name']))
            self.sql_session.flush()
        except IntegrityError as e:
            logging.info(f'{e}')
            state = 'error'
            message = '型號名稱重複!'
            code = 409
        except Exception as e:
            message = '連線不穩定，請在試一次!'
            state = f'error {e}'
            code = 500
        
        return {'message': message, 'state': state}, code

    def _get_c_id(self):
        cur_c_id = self.sql_session.query(SeatCategory.c_id) \
                                   .order_by(SeatCategory.c_id.desc()) \
                                   .first().c_id
        return cur_c_id + 1
    
    @login_check
    @role_required.permission(1)
    def put(self):
        '''修改型號名稱'''
        message, state, code = 'success', 'ok', 200
        type_data = request.json
        try:
            res = self.sql_session.query(SeatCategory) \
                                  .filter(SeatCategory.c_id == type_data['c_id']) \
                                  .update({SeatCategory.type_name: type_data['type_name']})
            message = f"成功更新{res}筆型號"
        except IntegrityError as e:
            logging.info(f'{e}')
            message = '型號名稱重複!'
            state = 'error'
            code = 409
        
        except Exception as e:
            message = '連線不穩定，請在試一次!'
            state = 'error'
            code = 500
        
        return {'message': message, 'state': state}, code

    @login_check
    @role_required.permission(1)
    def delete(self):
        '''刪除型號'''
        message, state, code = 'success', 'ok', 200
        c_id = request.args.get('c_id')
        try:
            seat_count = self.sql_session.query(func.count(SensorSeat.id).label('s_count')) \
                                         .filter(SensorSeat.seat_type == c_id) \
                                         .first().s_count
            record_count = self.sql_session.query(func.count(SensorRecord.id).label('r_count')) \
                                           .filter(SensorRecord.seat_type == c_id) \
                                           .first().r_count

            if any([seat_count, record_count]):
                raise ValueError

            res = self.sql_session.query(SeatCategory) \
                                  .filter(SeatCategory.c_id == c_id) \
                                  .delete()

            message = f"已刪除{res}筆型號"

        except IntegrityError as e:
            logging.info(f'{e}')
            message = '型號名稱重複!'
            state = 'error'
            code = 409
        
        except ValueError:
            message = '該型號已被使用過，無法刪除!'
            state = 'error'
            code = 409
        
        except Exception as e:
            message = '連線不穩定，請在試一次!'
            state = 'error'
            code = 500
        
        return {'message': message, 'state': state}, code
