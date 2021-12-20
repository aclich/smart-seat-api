from flask_restful import Resource
from flask import current_app
from api.conf.auth import login_check
from api.models.models import Blacklist

class TestDBSession(Resource):
    
    def __init__(self) -> None:
        super().__init__()
        self.sql_session = current_app.sql_session
    
    @login_check
    def get(self):
        blacklist = self.sql_session.query(Blacklist).all()
        print(blacklist)
        return {'message':"success", 'data':'test ok' }, 200