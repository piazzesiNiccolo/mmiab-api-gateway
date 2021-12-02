from datetime import datetime
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

    @classmethod
    def get_received_message_by_id_user(cls,id_usr):
        """
        Returns the list of sent messages by a specific user.
        """
        try:
            url = "%s/message/list/received/%s" % (cls.users_endpoint(),str(id_usr))
            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            obj = response.json()['messages']
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return code,obj

    @classmethod
    def get_drafted_message_by_id_user(cls,id_usr):
        """
        Returns the list of drafted messages by a specific user.
        """
        try:
            url = "%s/message/list/drafted/%s" % (cls.users_endpoint(),str(id_usr))
            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            obj = response.json()['messages']
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return code,obj

    @classmethod
    def get_timeline_day_mess_sent(cls,id_usr: int, year: int, month: int, day: int):

        try:
            url = "%s/message/list/sent/%s/%s/%s/%s" % (cls.users_endpoint(),str(id_usr),str(year),str(month),str(day))
            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            obj = response.json()['messages']
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return code,obj

    @classmethod
    def get_sended_message_by_id_user(cls,id_usr: int, data: datetime):
        """
        Returns the list of sent messages by a specific user.
        """
        try:
            if data is None:
                url = "%s/message/list/sent/%s" % (cls.users_endpoint(),str(id_usr))
            else:
                data_format = 'y=%d&m=%d&d=%d' % (data.year,data.month,data.day)
                url = "%s/message/list/sent/%s?%s" % (cls.users_endpoint(),str(id_usr),data_format)

            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            obj = response.json()['messages']
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return code,obj