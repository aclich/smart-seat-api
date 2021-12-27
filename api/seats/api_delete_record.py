#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

from flask import session, current_app
from flask_restful import Resource, request
import api.error.errors as error
from api.conf.auth import login_check
from api.models.models import SeatCategory, SensorRecord, SensorSeat
from sqlalchemy import func


class ApiDeleteRecord(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.sql_session = current_app.sql_session

    def get(self):
        return None

    @login_check
    def delete(self):
        mode = request.args.get('mode', default='', type=str)
        if mode == '':
            return error.INVALID_INPUT_422()
        if mode == 's':
            data_id = request.args.get('data_id', default=None)
            if data_id is None:
                return error.INVALID_INPUT_422()
            res = self.delete_single_data(data_id)
        elif mode == 'md':
            date = request.args.get('date', default=None)
            seat_id = request.args.get('seat_id', default=None)
            data_type = request.args.get('type', default=None)
            if any([i is None for i in [date, seat_id, data_type]]):
                return error.INVALID_INPUT_422()
            res = self.delete_data_by_date(seat_id, data_type, date)
        else:
            return error.INVALID_INPUT_422()
        return res

    def delete_single_data(self, data_id):
        status, message, code = 'success', '', 200
        try:
            del_q: SensorRecord = self.sql_session.query(SensorRecord) \
                                      .filter(SensorRecord.id == data_id)
            seat_q: SensorSeat = self.sql_session.query(SensorSeat) \
                                     .filter(SensorSeat.id == del_q.first().seat_id) \
                                     .first()
            if seat_q.user_id != session.user_id:
                return error.UNAUTHORIZED()
            del_q.delete()
            self.sql_session.flush()
            message = f'已成功刪除該筆資料!'
        except Exception as e:
            self.sql_session.rollback()
            message = f'刪除記錄失敗, data_id={data_id}, {e} '
            status = 'error'
            code = 500
        return ({'message': message, 'status': status}, code)

    def delete_data_by_date(self, seat_id, data_type, date):
        status, message, code = 'success', '', 200
        re_type_map = SeatCategory.get_type_map_reverse()
        try:
            seat_q: SensorSeat = self.sql_session.query(SensorSeat).filter(SensorSeat.id == seat_id).first()
            if seat_q.user_id != session.user_id:
                return error.UNAUTHORIZED()
            created_date = func.date(SensorRecord.created).label('created_date')
            del_res = self.sql_session.query(SensorRecord) \
                                    .filter(created_date == date,
                                            SensorRecord.seat_id == seat_id,
                                            SensorRecord.seat_type == re_type_map[data_type])\
                                    .delete(synchronize_session=False)
            self.sql_session.flush()
            message = f'已成功刪除 {date} 中 {del_res} 筆資料'
        except Exception as e:
            self.sql_session.rollback()
            status = 'error'
            message = f'刪除紀錄失敗, seat_id={seat_id}, data_type:{data_type}, date={date}, err:{e}'
            code = 500
        return ({'message': message, 'status': status}, code)