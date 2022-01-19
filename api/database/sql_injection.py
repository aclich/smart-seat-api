# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from distutils.sysconfig import customize_compiler
from email import message
import re
from api.conf.config import DB_NAME, SQL_HOST, SQL_PASSWD, SQL_PORT, SQL_USER
from flask import request
from flask_restful import Resource
from api.conf.auth import login_check
from api.roles import role_required
import pymysql

def post_process(val):
    if isinstance(val, datetime):
        val = datetime.strftime(val, "%Y-%m-%d %H:%M:%S")
    elif isinstance(val, date):
        val = date.strftime(val, "%Y-%m-%d")
    elif isinstance(val, timedelta):
        val = f"{val}"
    return val


class SqlInjection(Resource):
    def __init__(self) -> None:
        try:
            mysqldb = pymysql.connect(
                host= SQL_HOST,
                port= int(SQL_PORT),
                user=SQL_USER,
                passwd=SQL_PASSWD,
                database=DB_NAME
            )
            self.db_connection = mysqldb
        except Exception as e:
            raise Exception(f"DB連接失敗! {e}")

    @login_check
    @role_required.permission(2)
    def post(self):
        try:
            sql_cmd = request.json.get('sql_cmd')
            if "SELECT" not in sql_cmd.upper():
                raise Exception("Only can use SELECT command!")
            if any(c in ["ALTER", "DELETE", "CREATE", "INSERT", "UPDATE", "DROP"] 
                   for c in sql_cmd.upper().replace("\n"," ").split(' ')):
                raise Exception("Only can use SELECT command!")
            sql_cmd = " ".join(sql_cmd.split())
            cursor = self.db_connection.cursor()
            cursor.execute(sql_cmd)
            title = [col[0] for col in cursor.description]
            data = cursor.fetchall()
            result = [{title[idx]: post_process(val) for idx, val in enumerate(r)} for r in data]
            message = 'OK'
        except Exception as e:
            result=""
            message = f"Error occur!, error message:{e}"

        return {"message": message, 'data': result}, 200