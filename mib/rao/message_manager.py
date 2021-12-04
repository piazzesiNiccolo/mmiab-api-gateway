from datetime import datetime
from mib import app
from mib.rao.message import Message
from typing import List
from typing import Tuple

import requests


class MessageManager:

    @classmethod
    def message_endpoint(cls):
        return app.config['MESSAGES_MS_URL']
    
    @classmethod
    def requests_timeout_seconds(cls):
        return app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def read_message(cls, id_mess: int, id_usr: int) -> Tuple[int, Message, str]:
        try:
            url = "%s/message/%s/read/%s" % (cls.message_endpoint(), str(id_mess),str(id_usr))
            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            obj = Message.build_from_json(response.json()['obj'])
            message = response.json()['message']
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, None, "Unexpected response from messages microservice!"

        return code, obj, message

    @classmethod
    def retrieve_received_messages(cls,id_usr:int , data: datetime) -> Tuple[int, List[Message]]
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
            obj = [Message.build_from_json(m) for m in response.json()['messages']]
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, []

        return code,obj

    @classmethod
    def retrieve_drafts(cls, id_usr: int) -> Tuple[int, List[Message]]:
        """
        Returns the list of drafted messages by a specific user.
        """
        try:
            url = "%s/message/list/drafted/%s" % (cls.users_endpoint(),str(id_usr))
            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            obj = [Message.build_from_json(m) for m in response.json()['messages']]
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, []

        return code,obj

    @classmethod
    def retrieve_sent_messages(cls,id_usr: int, data: datetime) -> Tuple[int, List[Message]]:
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
            obj = [Message.build_from_json(m) for m in response.json()['messages']]
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, []

        return code,obj
