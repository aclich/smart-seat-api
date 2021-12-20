#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from typing import List

from flask import session, request, make_response, current_app
from flask_restful import Resource
import api.error.errors as error
from api.conf.auth import login_check
from api.models.models import SeatCategory, SensorSeat, SensorRecord, query_to_dict
from api.roles import role_required
from sqlalchemy.exc import IntegrityError, DataError
import json


class APISmartSeat(Resource):
    def __init__(self) -> None:
        self.sql_session = current_app.sql_session

    @login_check
    def get(self):
        query_list: list = self.sql_session.query(SensorSeat).filter(SensorSeat.user_id==session.user_id).all()
        seat_list = []
        for q in query_list:
            seat_list.append(query_to_dict(q))

        return {"message": "success", "data": seat_list}, 200
    
    @login_check
    def post(self):
        seat_data = request.json.get('data')
        user_data={'email': session.user_email, 'id': session.user_id}
        try:
            new_seat_dict = {
                'user_id': session.user_id,
                'seat_name': seat_data['seat_name'],
                'seat_type': int(seat_data['seat_type']),
                'note': seat_data['note']
            }
            new_seat = SensorSeat(**new_seat_dict)
            self.sql_session.add(new_seat)
            self.sql_session.flush()
        except IntegrityError as e:
            logging.log(1,f'{e}')
            return error.ALREADY_EXIST('坐墊名稱重複!')
        except DataError as e:
            return error.INVALID_INPUT_422('輸入資料長度過長!(不能超過255個字元)')

        except Exception as e:
            return {'message': 'failed', "user":user_data, 'data': seat_data, 'err_msg': f'{e}'}, 500
        return {"message": "success", "user":user_data, "data": seat_data}, 200

    @login_check
    def put(self):
        message, code, err_msg = 'success', 200, ''
        try:
            # c_id = request.args.get('c_id')
            seat_data = request.json.get('data')
            c_id = seat_data['id']
            seat_q: SensorSeat = self.sql_session.query(SensorSeat) \
                                     .filter(SensorSeat.id == c_id) \
                                     .first()
            if seat_q is None:
                raise Exception('發生錯誤,查無此坐墊!')
            if seat_q.user_id != session.user_id:
                raise Exception('Not your seats!!')
            seat_data['seat_type'] = self.sql_session.query(SeatCategory)\
                                         .filter(SeatCategory.type_name == seat_data['seat_type']) \
                                         .first().c_id

            if all([seat_data['seat_name'] == seat_q.seat_name,
                    seat_data['seat_type'] == seat_q.seat_type,
                    seat_data['note'] == seat_q.note]):
                return {'message': message, 'data': '', 'err_msg': '沒有更新'}, code

            res = self.sql_session.query(SensorSeat) \
                                     .filter(SensorSeat.id == c_id) \
                                     .filter(SensorSeat.user_id == session.user_id)\
                                     .update({
                                        SensorSeat.seat_name: seat_data['seat_name'],
                                        SensorSeat.seat_type: seat_data['seat_type'],
                                        SensorSeat.note: seat_data['note']
                                        })
            if res != 1:
                raise Exception('update error!')
            self.sql_session.flush()
        
        except IntegrityError as e:
            self.sql_session.rollback()
            message = 'failed'
            code = 409
            err_msg = '坐墊名稱已重複!'

        except Exception as e:
            self.sql_session.rollback()
            message = 'failed'
            code = 409
            err_msg = f'{e}'
        return {'message': message, 'data':'', 'err_msg': err_msg}, code

    @login_check
    def delete(self):
        seat_id = request.json.get('id')
        message, code, err_msg = 'success', 200, ''
        try:
            seat_q: SensorSeat = self.sql_session.query(SensorSeat) \
                            .filter(SensorSeat.id == seat_id) \
                            .filter(SensorSeat.user_id == session.user_id) \
                            .first()
            if seat_q is None:
                return error.NOT_FOUND_404('Not Your Sensor!')
            del_record: int = self.sql_session.query(SensorRecord) \
                                  .filter(SensorRecord.sensor_id == seat_id)\
                                  .delete()
            del_seat: int = self.sql_session.query(SensorSeat) \
                                            .filter(SensorSeat.id == seat_id) \
                                            .delete()

            if del_seat != 1:
                raise Exception('Deleted sensor count abnormal!')
            err_msg = f"坐墊已刪除，並已連帶刪除 {del_record} 筆量測紀錄資料!"

        except Exception as e:
            self.sql_session.rollback()
            message, code, err_msg = 'failed', 409, f'{e}'

        return {'message': message, 'data': '', 'err_msg': err_msg}, code


class GetTypeList(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.sql_session = current_app.sql_session

    @login_check
    def get(self):
        query_list: List[SeatCategory] = self.sql_session.query(SeatCategory).all()
        type_list = [{'value': '', 'text': '請選擇型號...'}]
        for q in query_list:
            type_list.append(
                {'value': q.c_id, 'text': f"{q.type_name}型"}
            )
        return {'message': 'success', 'data': type_list}, 200


    
    