#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from typing import List
import math
from flask import session, request, make_response, current_app
from flask_restful import Resource
from sqlalchemy.types import Date, Time
import api.error.errors as error
from api.conf.auth import login_check
from api.models.models import SeatCategory, SensorSeat, SensorRecord, query_to_dict, get_type_name
from api.roles import role_required
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy import func
import random
import json

class SearchRecrodDataService(object):
    def __init__(self) -> None:
        super().__init__()
        self.sql_session = current_app.sql_session
        self.type_map: dict = SeatCategory.get_type_map()

    def get_record_data_info(self, data_type: str, seat_id: str, date: str):
        seat_q: SensorSeat = self.sql_session.query(SensorSeat) \
                                            .filter(SensorSeat.id == seat_id) \
                                            .first()
        if (seat_name:= getattr(seat_q, 'seat_name', None)) is None:
            raise ("查無對應坐墊!")
        if seat_q.user_id != session.user_id:
            raise PermissionError("無權限查詢此坐墊資料!")

        min_time = func.min(func.time(SensorRecord.created)).label('min_time')
        max_time = func.max(func.time(SensorRecord.created)).label('max_time')
        data_count = func.count(SensorRecord.data).label('data_count')
        created_date = func.date(SensorRecord.created).label('created_date')
        record_q = self.sql_session.query(min_time,
                                          max_time,
                                          data_count) \
                                   .filter(SensorRecord.seat_id == int(seat_id),
                                           SensorRecord.seat_type == int(data_type),
                                           created_date == date) \
                                   .first()
        if record_q is None:
            raise Exception("查無資料!")
        
        return {'seat_id':seat_id, 
                'seat_name': seat_name, 
                'type': data_type,
                'time': f"{date}, {record_q.min_time}~{record_q.max_time}",
                'count': record_q.data_count  }

    def get_record_detail(self, data_type, seat_id, search_date, data_count):
        created_date = func.date(SensorRecord.created).label('created_date')
        record_q_list: List[SensorRecord] = \
            self.sql_session.query(SensorRecord) \
                            .filter(SensorRecord.seat_id == seat_id,
                                    SensorRecord.seat_type == data_type,
                                    created_date == search_date) \
                            .order_by(SensorRecord.created.asc()) \
                            .all()
        if len(record_q_list) != data_count:
            raise ValueError("資料筆數錯誤! SQL command might be wrong!")
        records_slider = {}
        slider = {'data': []}
        records_list = []
        for q in record_q_list:
            m_key = datetime.strftime(q.created, "%H:%M:%S")
            slider['data'].append(m_key)
            data_dict = {'data_id': q.id,
                         'time': f'{q.created}',
                         'data':q.data,
                         'posture': q.sitting_posture}
            records_slider[m_key] = data_dict
            records_list.append(data_dict)
        slider['range'] = self.get_slider_range(records_list)
        slider['value'] = slider['data'][0]
        slider_data = {
            'records_slider': records_slider,
            'slider': slider
        }
        return records_list, slider_data

    @staticmethod
    def get_slider_range(records_list):
        step = len(records_list) / 4
        slider_range = []
        for i in range(5):
            idx = math.ceil(i * step) - 1 if i > 0 else 0
            time_p = datetime.strptime(records_list[idx]['time'], "%Y-%m-%d %H:%M:%S")
            time = datetime.strftime(time_p, "%H:%M")
            slider_range.append({'label': time})
        return slider_range

    def get_chart_data(self, data_type, seat_id, search_date):
        pos_map = {
            'regular': '標準',
            'bias_right': '偏右',
            'bias_left': '偏左',
            'cross_right': '右腳翹二郎腿',
            'cross_left': '左腳翹二郎腿',
            'stand_on': '雙腳在椅子上'
        }
        created_date = func.date(SensorRecord.created).label('created_date')
        data_count = func.count(SensorRecord.data).label('data_count')
        pos_q = self.sql_session.query(SensorRecord.sitting_posture, data_count) \
                                .filter(created_date == search_date,
                                        SensorRecord.seat_id == seat_id,
                                        SensorRecord.seat_type == data_type) \
                                .group_by(SensorRecord.sitting_posture) \
                                .all()
        chart_data = [['posture', 'count']]
        for pos, cnt in pos_q:
            chart_data.append([pos_map[pos], cnt])
        return chart_data