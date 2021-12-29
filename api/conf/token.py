#!/usr/bin/python
# -*- coding: utf-8 -*-
from itsdangerous import TimedJSONWebSignatureSerializer as JsonWebToken
from flask_httpauth import HTTPTokenAuth
from .config import JWT_SECRET_KEY, REFRESH_SECRET_KEY

# JWT creation.
jwt_secret_key = JWT_SECRET_KEY
jwt = JsonWebToken(jwt_secret_key, expires_in=3600)

# Refresh token creation.
refresh_jwt = JsonWebToken(REFRESH_SECRET_KEY, expires_in=7200)

# Auth object creation.
auth = HTTPTokenAuth("Bearer")