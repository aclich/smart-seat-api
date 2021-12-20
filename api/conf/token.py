#!/usr/bin/python
# -*- coding: utf-8 -*-
from itsdangerous import TimedJSONWebSignatureSerializer as JsonWebToken
from flask_httpauth import HTTPTokenAuth

# JWT creation.
jwt_secret_key = "top secret!"
jwt = JsonWebToken(jwt_secret_key, expires_in=3600)

# Refresh token creation.
refresh_jwt = JsonWebToken("telelelele", expires_in=7200)

# Auth object creation.
auth = HTTPTokenAuth("Bearer")