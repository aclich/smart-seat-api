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
from sqlalchemy import func
import json


class ApiDashboard(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.sql_session = current_app.sql_session

    @login_check
    def get(self):
        subq_1 = self.sql_session.query(func.count(SensorSeat.id).label('s_count')) \
                                     .filter(SensorSeat.user_id == session.user_id) \
                                     .subquery()

        seat_count = self.sql_session.query(subq_1).first().s_count

        record_count = self.sql_session.query(func.count(SensorRecord.id).label('r_count')) \
                                       .filter(SensorSeat.user_id == session.user_id) \
                                       .join(SensorSeat, SensorSeat.id == SensorRecord.seat_id) \
                                       .first().r_count
        return {'message': 'ok', 'data': {'seat_count': seat_count, 'record_count': record_count}}