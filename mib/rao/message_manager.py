import os
from config import Config
from werkzeug.wrappers import response
from mib.auth.user import User
from mib import app
from flask_login import logout_user
from flask_login import current_user
from flask import abort
from flask.globals import current_app
import requests
from typing import List
from typing import Tuple
from uuid import uuid4


class MessageManager:

    @classmethod
    def users_endpoint(cls):
        return app.config['USERS_MS_URL']
    
    @classmethod
    def requests_timeout_seconds(cls):
        return app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def read_message(cls, id_mess, id_usr):
        try:
            url = "%s/message/%s/read/%s" % (cls.users_endpoint(), str(id_mess),str(id_usr))
            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            obj = response.json()['message']
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return code, obj
        