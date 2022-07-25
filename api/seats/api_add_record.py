#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from datetime import date, datetime, timedelta
from typing import List

from flask import session, request, make_response, current_app
from flask_restful import Resource
import api.error.errors as error
from api.conf.auth import login_check
from api.models.models import SeatCategory, SensorSeat, SensorRecord, query_to_dict
from api.roles import role_required
from sqlalchemy.exc import IntegrityError, DataError
import random

import json

FD_MAP= {
    1: {
        "regular" : [158, 612, 885, 720, 220, 660, 980, 1020, 994, 593, 850, 970, 1023, 980, 880, 720, 680, 340, 630, 750, 720, 650, 320, 621, 687 ],
        "bias_right" : [650, 783, 566, 340, 58, 1011, 1005, 998, 681, 123, 1023, 1023, 1001, 945, 210, 599, 340, 640, 690, 88, 612, 321, 555, 723, 94],
        "bias_left" : [112, 180, 390, 850, 641, 123, 399, 912, 946, 999, 200, 987, 1023, 1018, 1023, 212, 700, 682,  338, 660, 321, 888, 648, 289, 659],
        "cross_right" : [282, 612, 632, 641, 247, 555, 1023, 1020, 1015, 681, 681, 1023, 1023, 1023, 653, 351, 363, 847, 921, 632, 350, 320, 944, 931, 590],
        "cross_left" : [123, 589, 570, 530, 311, 666, 1023, 1023, 1020, 960, 631, 1023, 1023, 1023, 611, 669, 899, 913, 645, 632, 645, 888, 891, 320, 530],
        "stand_on" : [412, 1023, 1023, 1023, 521, 488, 1023, 1023, 1023, 600, 400, 1023, 1023, 1023, 444, 1023, 1023, 1023, 432, 599, 1023, 1023, 1023, 483]
    },

    2: {
    "regular" : [187, 356, 388, 142, 591, 862, 831, 431, 444, 980, 974, 660, 591, 783, 989, 599, 352, 721, 789, 671, 320, 623, 689, 311],
    "bias_right" : [599, 671, 471, 189, 1023, 1023, 582, 299, 788, 921, 355, 280, 1023, 1023, 541, 312, 799, 1011, 561, 288, 1023, 699, 640, 317],
    "bias_left" : [312, 388, 478, 624, 288, 412, 932, 974, 246, 246, 841, 735, 288, 561, 912, 932, 103, 496, 1023, 1023, 121, 631, 899, 912],
    "cross_right" : [312, 388, 432, 189, 350, 788, 982, 534, 412, 941, 1023, 681, 350, 1023, 1023, 660, 350, 589, 871, 613],
    "cross_left" : [338, 489, 521, 284, 645, 1023, 1023, 603, 574, 1001, 1011, 549, 471, 974, 831, 512, 431, 1008, 1002, 441, 491, 911, 280, 211],
    "stand_on" : [667, 999, 974, 456, 660, 1023, 1023, 683, 741, 941, 1023, 1023, 961, 843, 861, 1023, 1023, 799, 1023, 1021, 1020, 1008, 1001, 890]
    }
}

class ApiAddRecord(Resource):
    def __init__(self) -> None:
        super().__init__()

    @login_check
    def post(self):
        pass

class ApiUploadRecordJson(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.sql_session = current_app.sql_session

    @login_check
    def post(self):
        try:
            req_body = request.json
            if not isinstance(req_body, list):
                return {'message': "error", 'data': 'upload failed, json data should be list'}
            suc, bad, err_data = self._upload_json_record(req_body)
            return {"message": "success", "data": f"uploaded {suc} data, failed {bad} data", "err_msg": err_data}, 200
        
        except Exception as e:
            return error.SERVER_ERROR_500(f'{e}')
    
    def _upload_json_record(self, json_data):
            err_line = []
            for record in json_data:
                try:
                    new_record = SensorRecord(
                            seat_id=record['seat_id'],
                            seat_type=record['seat_type'],
                            data=str(record['data']),
                            sitting_posture=record['sit_pos'],
                            gender=str(record['gender']),
                            height=record['height'],
                            weight=record['weight'],
                            created=datetime.strptime(record['time'], "%Y%m%d %H:%M:%S")
                        )
                    # query = SensorRecord.query.filter_by(new_record)
                    # if query:
                    #     raise Exception("資料重複")

                    self.sql_session.add(new_record)
                except KeyError as e:
                    err_line.append({'data': record, "err_msg": f"missing key: {e}"})
                except Exception as e:
                    err_line.append({'data': record, "err_msg": f"data error: {e}"})
            try:
                self.sql_session.flush()
            except IntegrityError as e:
                err_msg = f"查無seat_id: {json_data[0]['saet_id']}" \
                if "a foreign key constraint fails" in f'{e}' else f'與資料庫連線不穩定 {e}'
                raise Exception(err_msg)
            
            except Exception as e:
                self.sql_session.rollback()
                raise Exception(f"{e}")
                
            
            return len(json_data) - len(err_line), len(err_line), err_line

        

        
class ApiGenerateData(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.sql_session = current_app.sql_session
    
    @login_check
    def post(self):
        try:
            req_body = request.json.get('data')
            rec_day, gen_num = self.gen_random_data(req_body)
        except Exception as e:
            return error.SERVER_ERROR_500(f'{e}')
        return {"message": "success", "data": f"Generated {gen_num} records in {rec_day}"}
        
    def gen_random_data(self,seat_data):
        rec_day = datetime.now() - timedelta(days=random.randint(0,10),
                                             hours=random.randint(0,24),
                                             minutes=random.randint(0,59),
                                             seconds=random.randint(0,59))
        for i in range(random.randint(5,55)):
            seat_type = seat_data['seat_type'] if seat_data['seat_type'] < 3 else 1
            sitting_posture, sensor_data = random.choice(list(FD_MAP[seat_type].items()))
            record_dict = {
                'seat_id': seat_data['id'],
                'seat_type': seat_data['seat_type'],
                'data': str(sensor_data),
                'sitting_posture': sitting_posture,
                'created': rec_day + timedelta(minutes= i * 5, seconds=random.randint(10,75))
            }
            self.sql_session.add(SensorRecord(**record_dict))
        self.sql_session.flush()
        return datetime.strftime(rec_day, "%Y-%m-%d %H:%M:%S"), i+1
