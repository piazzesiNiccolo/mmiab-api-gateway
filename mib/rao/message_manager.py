from datetime import datetime
from mib import app

from flask_wtf import FlaskForm
from flask_login import logout_user
from flask_login import current_user
from flask import abort
from flask.globals import current_app as app
import base64
import json
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

    
    '''@classmethod
    def get_message(cls, id_message, id_user):

        endpoint = '%s/message/%s/%s' % (cls.message_endpoint(cls), str(id_message), str(id_user))
        try:
            response = requests.get(endpoint, timeout=cls.requests_timeout_seconds())
            message = response.json()
            return response.status_code, message
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, None'''
    

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
    def reply_to_message(cls, id_message: int, id_user: int):
        url = f'{cls.message_endpoint()}/message/reply/{id_message}/{id_user}'
        try:
            response = requests.post(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            message = response.json()['message']
        except:
            return 500, "Unexpected response from messages microservice!"

        return code, message

    @classmethod
    def forward_message(cls, id_message: int, id_user: int):
        url = f'{cls.message_endpoint()}/message/forward/{id_message}/{id_user}'
        try:
            response = requests.post(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            message = response.json()['message']
            obj = None
            if code == 200:
                obj = Message.build_from_json(response.json()['obj'])
        except:
            return 500, None, "Unexpected response from messages microservice!"

        return code, obj, message

    @classmethod
    def get_message(cls, id_mess: int, id_usr: int) -> Tuple[int, Message, str]:
        obj = None
        try:
            url = "%s/message/%s/%s" % (cls.message_endpoint(), str(id_mess),str(id_usr))
            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            _json = response.json()
            if code == 200:
                msg = Message.build_from_json(_json['obj'])
                _users = _json['users']
                users = {int(k): v for k,v in _users.items()}
                image = _json['image']
                _rp_info = _json['replying_info']
                replying_info = cls.format_replying_info(_rp_info, users)
                obj = (msg, users, image, replying_info)
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
            if code == 200:
                obj = [Message.build_from_json(m) for m in response.json()['messages']]
                _senders = response.json()['senders']
                senders = {int(k): v for k,v in _senders.items()}
                _opened = response.json()['has_opened']
                opened = {int(k):v for k,v in _opened.items()}
            else:
                obj, senders, opened = [], {}, []
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, [], [], {}

        return code, obj, opened, senders

    @classmethod
    def retrieve_drafts(cls, id_usr: int) -> Tuple[int, List[Message]]:
        """
        Returns the list of drafted messages by a specific user.
        """
        try:
            url = "%s/message/list/draft/%s" % (cls.message_endpoint(),str(id_usr))
            response = requests.get(url, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            if code == 200:
                obj = [Message.build_from_json(m) for m in response.json()['messages']]
                _recipients = response.json()['recipients']
                recipients = {int(k): v for k,v in _recipients.items()}
            else:
                obj, recipients = [], {}
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, [], {}

        return code,obj,recipients

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
            code = response.status_code
            if code == 200:
                obj = [Message.build_from_json(m) for m in response.json()['messages']]
                _recipients = response.json()['recipients']
                recipients = {int(k): v for k,v in _recipients.items()}
            else:
                obj, recipients = [], {}
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, [], {}

        return code,obj,recipients

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
    def form_to_dict(cls, form: FlaskForm) -> dict:
        return {
            k: form.data[k] for k in form.data 
            if k not in ["csrf_token", "submit"] and form.data[k] is not None
        }

    @classmethod
    def format_draft_data(cls, form_data: dict, id_sender: int):
        for k in form_data:
            if k == "recipients":
                form_data[k] = [int(rf['recipient']) for rf in form_data[k]]
            elif k == "image":
                file = form_data["image"]
                b64_file = base64.b64encode(file.read()).decode("utf-8")

                form_data[k] =  {
                    'name': file.filename,
                    'data': b64_file,
                }
            elif k == 'delivery_date':
                try:
                    form_data[k] = form_data[k].strftime('%H:%M %d/%m/%Y')
                except AttributeError:
                    form_data[k] = None
        form_data['id_sender'] = id_sender
        return {k:v for k,v in form_data.items() if v is not None}

    @classmethod
    def post_draft(cls, form_data: dict, id_sender: int):

        cls.format_draft_data(form_data, id_sender) 
        try:
            url = "%s/draft" % (cls.message_endpoint())
            response = requests.post(url, json=form_data, timeout=cls.requests_timeout_seconds())
            code = response.status_code
            id_message = None
            if code == 201:
                id_message = response.json()['id_message']

            return code, id_message
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, None

    @classmethod
    def format_replying_info(cls, msg, users):
        if len(msg.keys()) > 0:
            message_body = msg['message_body']
            id_sender = int(msg['id_sender'])
            user_dict = users.get(id_sender, None)
            if user_dict is not None:
                _user = {
                    'id': id_sender,
                    'first_name': user_dict['first_name'],
                    'last_name': user_dict['last_name'],
                }
            else:
                _user = {
                    'id': 0,
                    'first_name': 'Anonymous',
                    'last_name': '',
                }

            return ({
                "message": {
                    "id_sender":id_sender,
                    "message_body":  message_body,
                    "delivery_date": msg['delivery_date']
                },
                "user": _user,
            })

        return None

    @classmethod
    def get_replying_info(cls, id_message: int, id_user: int):

        if id_message is not None:
            try:
                url = "%s/message/replying_info/%s/%s" % (cls.message_endpoint(), str(id_message),str(id_user))
                response = requests.get(url, timeout=cls.requests_timeout_seconds())
                code = response.status_code
                _json = response.json()
                if code == 200:
                    obj = _json['obj']
                    _users = _json['users']
                    users = {int(k): v for k,v in _users.items()}
                    return cls.format_replying_info(obj, users)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                return None

        return None

    @classmethod
    def put_draft(cls, form_data: dict, id_sender: int, id_message: int):

        cls.format_draft_data(form_data, id_sender)
        try:
            url = "%s/draft/%s/%s" % (cls.message_endpoint(), str(id_message), str(id_sender))
            response = requests.put(url, json=form_data, timeout=cls.requests_timeout_seconds())
            code = response.status_code

            return code
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500
