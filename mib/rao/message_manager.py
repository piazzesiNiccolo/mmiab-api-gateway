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

    USERS_ENDPOINT = Config.USERS_MS_URL
    REQUESTS_TIMEOUT_SECONDS = Config.REQUESTS_TIMEOUT_SECONDS

    @classmethod
    def read_message(cls, id_mess):
        try:
            url = "%s/read_message/%s" % (cls.USERS_ENDPOINT, str(id_mess))
            response = requests.get(url, timeout=cls.REQUESTS_TIMEOUT_SECONDS)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response
        