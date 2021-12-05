from datetime import datetime
from mib import app

from flask_login import logout_user
from flask_login import current_user
from flask import abort
from flask.globals import current_app as app
import base64
from mib.rao.message import Message
from mib.rao.timeline import Timeline
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

    '''
    @classmethod
    def get_message(cls, id_message, id_user) -> Tuple[int, str]:

        endpoint = '%s/message/%s/%s' % (cls.message_endpoint(cls), str(id_message), str(id_user))
        try:
            response = requests.get(endpoint, timeout=cls.requests_timeout_seconds())
            message = response.json()
            return response.status_code, message
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected reponse from user microservice"
    '''

    @classmethod
    def send_message(cls, id_message: int, id_user: int) -> Tuple[int, str]:
        endpoint = '%s/message/send/%s/%s' % (cls.message_endpoint(), str(id_message), str(id_user))
        try:
            response = requests.post(endpoint, timeout=cls.requests_timeout_seconds())
            message = response.json()["message"]
            return response.status_code, message
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected response from messages microservice!"

    '''
    @classmethod
    def get_draft(cls, id_message, id_user) -> Tuple[int, str]:
        #TODO:fix
        endpoint = '%s/message/%s/%s' % (cls.message_endpoint(), str(id_message), str(id_user))
        try:
            response = requests.get(endpoint, timeout=cls.requests_timeout_seconds())
            message = response.json()["message"]
            return response.status_code
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected reponse from user microservice"

    @classmethod
    def get_message(cls, id_message, id_user) -> Tuple[int, str]:

        endpoint = '%s/message/%s/%s' % (cls.message_endpoint(), str(id_message), str(id_user))
        try:
            response = requests.get(endpoint, timeout=cls.requests_timeout_seconds())
            message = response.json()["message"]
            return response.status_code
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected reponse from user microservice"
    '''

    @classmethod
    def delete_draft(cls, id_message: int, id_user: int):
        url = f'{cls.message_endpoint()}/draft/{id_message}/{id_user}'
        try:
            response = requests.delete(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            message = response.json()['message']
        except:
            return 500, "Unexpected response from messages microservice!"

        return code, message

    @classmethod
    def delete_read_message(cls, id_message: int, id_user: int):
        url = f'{cls.message_endpoint()}/message/{id_message}/{id_user}'
        try:
            response = requests.delete(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            message = response.json()['message']
        except:
            return 500, "Unexpected response from messages microservice!"

        return code, message

    @classmethod
    def withdraw_message(cls, id_message: int, id_user: int):
        url = f'{cls.message_endpoint()}/message/withdraw/{id_message}/{id_user}'
        try:
            response = requests.post(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            message = response.json()['message']
        except:
            return 500, "Unexpected response from messages microservice!"

        return code, message


    @classmethod
    def get_message(cls, id_mess: int, id_usr: int) -> Tuple[int, Message, str]:
        obj = None
        try:
            url = "%s/message/%s/read/%s" % (cls.message_endpoint(), str(id_mess),str(id_usr))
            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            _json = response.json()
            if code == 200:
                msg = Message.build_from_json(_json['obj'])
                users = _json['users']
                image = _json['image']
                obj = (msg, users, image)
            message = response.json()['message']
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, None, "Unexpected response from messages microservice!"

        return code, obj, message

    @classmethod
    def retrieve_received_messages(cls,id_usr:int , data: datetime = None) -> Tuple[int, List[Message]]:
        """
        Returns the list of received messages by a specific user.
        """
        try:
            if data is None:
                url = "%s/message/list/received/%s" % (cls.message_endpoint(),str(id_usr))
            else:
                data_format = 'y=%d&m=%d&d=%d' % (data.year,data.month,data.day)
                url = "%s/message/list/received/%s?%s" % (cls.message_endpoint(),str(id_usr),data_format)

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
            url = "%s/message/list/drafted/%s" % (cls.message_endpoint(),str(id_usr))
            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            obj = [Message.build_from_json(m) for m in response.json()['messages']]
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, []

        return code,obj

    @classmethod
    def retrieve_sent_messages(cls,id_usr: int, data: datetime = None) -> Tuple[int, List[Message]]:
        """
        Returns the list of sent messages by a specific user.
        """
        try:
            if data is None:
                url = "%s/message/list/sent/%s" % (cls.message_endpoint(),str(id_usr))
            else:
                data_format = 'y=%d&m=%d&d=%d' % (data.year,data.month,data.day)
                url = "%s/message/list/sent/%s?%s" % (cls.message_endpoint(),str(id_usr),data_format)

            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            print(response.json())
            code = response.status_code
            obj = [Message.build_from_json(m) for m in response.json()['messages']]
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, []

        return code,obj

    @classmethod
    def get_timeline_month(cls,id_usr: int, dt: datetime):
        try:
            data_format = 'y=%d&m=%d' % (dt.year,dt.month)
            url = "%s/timeline/list/%s?%s" % (cls.message_endpoint(),str(id_usr),str(data_format))
            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            timeline = Timeline.build_from_json(**response.json())
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, None

        return code, timeline

    @classmethod
    def post_draft(cls, form):

        form_dict = {}
        for k in form.data:
            if k not in ["csrf_token", "submit"] and form.data[k] is None:
                if k == "recipients":
                    form_dict.update({k : [int(rf.recipient.data[0]) for rf in form.recipients]})
                
                elif k == "image":
                    file = form["image"]
                    b64_file = base64.b64encode(file.read()).decode("utf8")

                    form_dict.update({k : {
                                'name': file.filename,
                                'data': b64_file,
                                }
                    })

                else:
                    form_dict.update({k : form.data})
        
        try:
            url = "%s/draft/" % (cls.message_endpoint())
            response = requests.post(url, data=form_dict, timeout=cls.requests_timeout_seconds())

            return response.status_code
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected response from messages microservice!"

    @classmethod
    def get_replying_info(cls, id_message: int, id_user: int):

        if id_message is not None:
            _, obj, _ = cls.get_message(id_message, id_user)
            if obj != None:
                message, users, _ = obj
                body_message = message.body_message
                user_dict = users.get(id_user, None)
                if user_dict is not None:
                    _fn, _ln = user_dict.get('first_name', None), user_dict.get('last_name', None)
                    user = _fn + ' ' + _ln if (_fn, _ln) != (None, None) else 'Anonymous'
                    return ({
                        "message": body_message,
                        "user": user,
                    })

        return None

