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

class MessageManager:

    @classmethod

    def message_endpoint(cls):
        return app.config['MESSAGES_MS_URL']
    
    @classmethod
    def requests_timeout_seconds(cls):
        return app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def get_message(cls, id_message, id_user) -> Tuple[int, str]:
        endpoint = '%s/message/%s/%s' % (cls.users_endpoint(cls), str(id_message), str(id_user))
        try:
            response = requests.get(endpoint, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            message = response.json()
            return response.status_code, message
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected reponse from user microservice"

    @classmethod
    def send_message(cls, id_message, id_user) -> Tuple[int, str]:
        endpoint = '%s/message/send/%s/%s' % (cls.users_endpoint(cls), str(id_message), str(id_user))
        try:
            response = requests.post(endpoint, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            message = response.json()["message"]
            return response.status_code, message
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected reponse from user microservice"

    @classmethod
    def delete_draft(cls, id_message, id_user) -> Tuple[int, str]:
        endpoint = '%s/message/%s/%s' % (cls.users_endpoint(cls), str(id_message), str(id_user))
        try:
            response = requests.delete(endpoint, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            message = response.json()["message"]
            return response.status_code, message
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected reponse from user microservice"

    @classmethod
    def get_draft(cls, id_message, id_user) -> Tuple[int, str]:
        #TODO:fix
        endpoint = '%s/message/%s/%s' % (cls.users_endpoint(cls), str(id_message), str(id_user))
        try:
            response = requests.get(endpoint, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            message = response.json()["message"]
            return response.status_code
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected reponse from user microservice"

    @classmethod
    def get_message(cls, id_message, id_user) -> Tuple[int, str]:
        #TODO:fix
        endpoint = '%s/message/%s/%s' % (cls.users_endpoint(cls), str(id_message), str(id_user))
        try:
            response = requests.get(endpoint, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            message = response.json()["message"]
            return response.status_code
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected reponse from user microservice"

    def read_message(cls, id_mess, id_usr):
        try:
            url = "%s/message/%s/read/%s" % (cls.message_endpoint(), str(id_mess),str(id_usr))
            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            obj = response.json()['message']
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected response from messages microservice!"

        return code, obj

    @classmethod
    def get_received_message_by_id_user(cls,id_usr:int , data: datetime):
        """
        Returns the list of received messages by a specific user.
        """
        try:
            if data is None:
                url = "%s/message/list/received/%s" % (cls.users_endpoint(),str(id_usr))
            else:
                data_format = 'y=%d&m=%d&d=%d' % (data.year,data.month,data.day)
                url = "%s/message/list/received/%s?%s" % (cls.users_endpoint(),str(id_usr),data_format)

            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            obj = response.json()['messages']
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected response from messages microservice!"

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
            print(response.json())
            code = response.status_code
            obj = response.json()['messages']
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected response from messages microservice!"

        return code,obj
