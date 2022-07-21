#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask_restful import Api
from api.admin.api_seat_type_management import ApiSeatTypeManagement
from api.admin.api_user_management import ApiUserManagement

from api.handlers.UserHandlers import (
    DataAdminRequired,
    DataUserRequired,
    Index,
    Login,
    Logout,
    RefreshToken,
    Register,
    ResetPassword,
    UsersData,
    DataSuperAdminRequired)

from api.database.test_dbsession import TestDBSession
from api.database.sql_injection import SqlInjection
from api.handlers.user_edit import ApiUserEdit
from api.seats.api_add_record import ApiGenerateData, ApiUploadRecordJson
from api.seats.api_delete_record import ApiDeleteRecord
from api.seats.api_search_record import ApiGetRecordData, ApiGetSeatList, ApiGetSeatRecordList
from api.seats.seat_servce import APISmartSeat, GetTypeList
from api.api_dashboard import ApiDashboard

def generate_routes(app):

    # Create api.
    api = Api(app)

    # Add all routes resources.
    # Index page.
    api.add_resource(Index, "/")

    # Register page.
    api.add_resource(Register, "/auth/register")

    # Login page.
    api.add_resource(Login, "/auth/login")

    # Logout page.
    api.add_resource(Logout, "/auth/logout")

    # Refresh page.
    api.add_resource(RefreshToken, "/v1/auth/refresh")

    # Password reset page. Not forgot.
    api.add_resource(ResetPassword, "/v1/auth/password_reset")

    # Example user handler for user permission.
    api.add_resource(DataUserRequired, "/data_user")

    # Example admin handler for admin permission.
    api.add_resource(DataAdminRequired, "/data_admin")

    # Example user handler for user permission.
    api.add_resource(DataSuperAdminRequired, "/data_super_admin")

    # Get users page with admin permissions.
    api.add_resource(UsersData, "/users")

    #Test ORM
    api.add_resource(TestDBSession, "/t/ormsession")

    # Super user function, SQL injection
    api.add_resource(SqlInjection, "/s/mdkp4ga")

    #Seat management
    #Register Seat
    api.add_resource(APISmartSeat, "/seat/manage")
    api.add_resource(GetTypeList, "/seat/get-type-list")

    #Seat Data
    api.add_resource(ApiGetSeatList, "/seat/get-seat-list")
    api.add_resource(ApiGetSeatRecordList, "/seat/get-record-list/<seat_id>")
    api.add_resource(ApiGetRecordData, "/seat/get-data/<data_type>/<seat_id>/<search_date>")
    api.add_resource(ApiDeleteRecord, "/seat/delete-data")
    api.add_resource(ApiGenerateData, "/seat/data/auto-gen")
    api.add_resource(ApiUploadRecordJson,"/seat/data/upload-json/")

    #user_management
    api.add_resource(ApiUserManagement, '/admin/user_management')

    #seat_type_management
    api.add_resource(ApiSeatTypeManagement,'/admin/seat_type_management')

    #dashboard
    api.add_resource(ApiDashboard, '/dashboard')

    #user_edit
    api.add_resource(ApiUserEdit, '/user/edit')