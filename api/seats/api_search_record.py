#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

from flask import session, current_app
from flask_restful import Resource
import api.error.errors as error
from api.conf.auth import login_check
from api.models.models import SeatCategory, SensorSeat, SensorRecord

from sqlalchemy import func

from api.seats.biz.show_record_data import SearchRecrodDataService



class ApiGetSeatList(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.sql_session = current_app.sql_session
        self.type_map: dict = SeatCategory.get_type_map()
    
    @login_check
    def get(self):
        seats_query: List[SensorSeat] = self.sql_session.query(SensorSeat).filter(SensorSeat.user_id == session.user_id).all()
        seats_list = []
        for q in seats_query:
            # s_type:SeatCategory = self.sql_session.query(SeatCategory).filter(SeatCategory.c_id == q.seat_type).first()
            seats_list.append({
                'value': q.id,
                'text': f'{q.seat_name} / {self.type_map[q.seat_type]}型'
            })
        return {'message': 'success', 'data':seats_list}, 200

class ApiGetSeatRecordList(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.sql_session = current_app.sql_session
        self.type_map: dict = SeatCategory.get_type_map()

    @login_check
    def get(self, seat_id: str):
        message, code = 'success', 200
        try:
            seat_id = int(seat_id)
            seat_q: SensorSeat = self.sql_session.query(SensorSeat) \
                            .filter(SensorSeat.id == seat_id) \
                            .first()
            if seat_q is None:
                return error.NOT_FOUND_404('發生錯誤,查無此坐墊!')
            if seat_q.user_id != session.user_id:
                return error.INVALID_INPUT_422('Not your seats!!')
            seat_info = {
                'id': seat_id,
                'name': seat_q.seat_name,
                'type': self.type_map[seat_q.seat_type]
            }
            record_list = self.get_record_list(seat_id)

        except Exception as e:
            return error.SERVER_ERROR_500(f'{e}')

        return {'message': message, 'seat_info': seat_info, 'record_list': record_list}, code

    def get_record_list(self, seat_id):
        min_time = func.min(func.time(SensorRecord.created)).label('min_time')
        max_time = func.max(func.time(SensorRecord.created)).label('max_time')
        data_count = func.count(SensorRecord.data).label('data_count')
        created_date = func.date(SensorRecord.created).label('created_date')
        record_q: List[SensorRecord] = self.sql_session.query(SensorRecord.seat_type,
                                                              min_time,
                                                              max_time,
                                                              data_count,
                                                              created_date) \
                                                        .filter(SensorRecord.seat_id == int(seat_id)) \
                                                        .group_by(created_date, SensorRecord.seat_type) \
                                                        .order_by(created_date.desc()) \
                                                        .all()
        data_record= []
        for q in record_q:
            created = getattr(q, 'created_date', None)
            created = created if created is None else datetime.strftime(created, "%Y-%m-%d")
            data_record.append({
            "type": self.type_map.get(q.seat_type, None),
            "created": created,
            "time": '{}~{}'.format(getattr(q,'min_time', None), getattr(q, 'max_time', None)),
            "count": getattr(q, 'data_count', None)
            })
        return data_record

class ApiGetRecordData(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.data_sevice = SearchRecrodDataService()

    @login_check
    def get(self, data_type, seat_id, search_date):
        status, message, data, code = "success", "", {}, 200
        try:
            r_type_map = SeatCategory.get_type_map_reverse()
            data_type = r_type_map[data_type]
            record_data_info = self.data_sevice.get_record_data_info(data_type, seat_id, search_date)
            '''
            slider_data include:
            1. records_slider:
                slider data map
                format: {
                    "08:12:34": {data_id:0, time:"2021-12-12 08:12:34", data:[], posture:"regular"}
                    }
            2. slider:{
                value: first record time (HH:MM:SS),
                data:[ key of data map ],
                range:
                    5 timestamp (HH:MM) slice start from first, end in last record
                    format: [ {label: "08:12"}, {label: "09:12"} ]
            }
            '''
            records_list, slider_data = self.data_sevice.get_record_detail(data_type,
                                                                           seat_id,
                                                                           search_date,
                                                                           record_data_info['count'])
            chart_data = self.data_sevice.get_chart_data(data_type, seat_id, search_date)
            type_map = SeatCategory.get_type_map()
            data ={
                'record_data_info': record_data_info,
                'records_slider': slider_data.get('records_slider', None),
                'slider': slider_data.get('slider', None),
                'records_list': records_list,
                'chartData': chart_data,
                'type_map': type_map
            }

        except PermissionError as e:
            message = f'{e}'
            code = 401

        except Exception as e:
            message = f'{e}'
            code = 500
        
        status = 'success' if code == 200 else 'error'
        return {'message': message, 'status':status, 'data': data}, code



