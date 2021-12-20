#!/usr/bin/python
# -*- coding: utf-8 -*-

SERVER_ERROR_500 = ({"message": "An error occured."}, 500)
NOT_FOUND_404 = ({"message": "Resource could not be found."}, 404)
NO_INPUT_400 = ({"message": "No input data provided."}, 400)
INVALID_INPUT_422 = lambda message='Invalid Input': ({"message": message}, 422)
ALREADY_EXIST = lambda message='Data already exists': ({"message": message}, 409)
NOT_LOGIN = ({"message": "Please Login First!"}, 401)
UNAUTHORIZED = ({"message": "Wrong credentials."}, 401)

DOES_NOT_EXIST = lambda message="Does not exists.": ({"message": message}, 409)
NOT_ADMIN = ({"message": "Admin permission denied."}, 999)
HEADER_NOT_FOUND = ({"message": "Header does not exists."}, 999)
