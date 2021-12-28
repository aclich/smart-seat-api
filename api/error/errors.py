#!/usr/bin/python
# -*- coding: utf-8 -*-
from http import HTTPStatus


class BaseError(Exception):
    description = None
    code = None
    data = None
    http_status_code: HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, description, code=None, data=None):
        Exception.__init__(self, description)
        self.description = description
        self.code = code
        self.data = data


SERVER_ERROR_500 = lambda message="An error occured.": ({"message": message}, 500)
NOT_FOUND_404 = lambda message="Resource could not be found.": ({"message": message}, 404)
NO_INPUT_400 = lambda message="No input data provided.": ({"message": message}, 400)
INVALID_INPUT_422 = lambda message='Invalid Input': ({"message": message}, 422)
ALREADY_EXIST = lambda message='Data already exists': ({"message": message}, 409)
NOT_LOGIN = lambda message='Please Login First!':({"message": message}, 401)
UNAUTHORIZED = lambda message='Wrong credentials.': ({"message": message}, 401)

DOES_NOT_EXIST = lambda message="Does not exists.": ({"message": message}, 409)
NOT_ADMIN = lambda message="Admin permission denied.": ({"message": message}, 403)
HEADER_NOT_FOUND = lambda message="Header does not exists.": ({"message": message}, 400)
