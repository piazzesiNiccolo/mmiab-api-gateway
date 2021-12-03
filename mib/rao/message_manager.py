import requests
from typing import Tuple
from mib import app

class MessageManager:

    @classmethod
    def users_endpoint(cls):
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