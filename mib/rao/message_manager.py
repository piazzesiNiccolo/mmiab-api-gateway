
from flask.globals import current_app as app
import requests


class MessageManager:

    @classmethod
    def message_endpoint(cls):
        return app.config['MESSAGES_MS_URL']
    
    @classmethod
    def requests_timeout_seconds(cls):
        return app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
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
    def get_sended_message_by_id_user(cls,id_usr):
        """
        Returns the list of sent messages by a specific user.
        """
        try:
            url = "%s/message/list/sent/%s" % (cls.message_endpoint(),str(id_usr))
            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            print(response.json())
            code = response.status_code
            obj = response.json()['messages']
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected response from messages microservice!"

        return code,obj
