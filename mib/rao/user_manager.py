import os

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
from werkzeug.utils import secure_filename

class UserManager:
    USERS_ENDPOINT = app.config['USERS_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def get_users_list(cls, query: str, blacklist: bool = False) -> Tuple[List[User], int]:

        target = "blacklist" if blacklist else "users_list"
        endpoint = f"{cls.USERS_ENDPOINT}/{target}/{current_user.id}?q={query}"

        try:
            response = requests.get(endpoint, timeout=cls.REQUESTS_TIMEOUT_SECONDS)

            users = [ User.build_from_json(u) for u in response.json()['users'] ]
            return users, response.status_code

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

    @classmethod
    def get_user_by_id(cls, user_id: int) -> User:
        """
        This method contacts the users microservice
        and retrieves the user object by user id.
        :param user_id: the user id
        :return: User obj with id=user_id
        """
        try:
            response = requests.get("%s/user/%s" % (cls.USERS_ENDPOINT, str(user_id)),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            if response.status_code == 200:
                # user is authenticated
                user = User.build_from_json(json_payload)
            elif response.status_code == 404:
                user = None
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return user

    @classmethod
    def get_user_by_email(cls, user_email: str):
        """
        This method contacts the users microservice
        and retrieves the user object by user email.
        :param user_email: the user email
        :return: User obj with email=user_email
        """
        try:
            response = requests.get("%s/user_email/%s" % (cls.USERS_ENDPOINT, user_email),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            user = None

            if response.status_code == 200:
                user = User.build_from_json(json_payload)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return user

    @classmethod
    def get_user_by_phone(cls, user_phone: str) -> User:
        """
        This method contacts the users microservice
        and retrieves the user object by user phone.
        :param user_phone: the user phone
        :return: User obj with phone=user_phone
        """
        try:
            response = requests.get("%s/user_phone/%s" % (cls.USERS_ENDPOINT, user_phone),
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            user = None

            if response.status_code == 200:
                user = User.build_from_json(json_payload)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return user

    @classmethod
    def create_user( cls, form_data ):
        form_data['birthdate'] = form_data['birthdate'].strftime("%d/%m/%Y")

        if "profile_picture" in form_data.keys():
            file = form_data["profile_picture"]
            name = file.filename
            name = str(uuid4()) + secure_filename(name)

            path = os.path.join(current_app.config["UPLOAD_FOLDER"], name)
            form_data['profile_picture'] = name
            print('PIPPO', os.listdir('/static/assets'))
            file.save(path)
        else:
            form_data['profile_picture'] = "default.png"

        try:
            url = "%s/user" % cls.USERS_ENDPOINT
            response = requests.post(
                url,
                json=form_data,
                timeout=cls.REQUESTS_TIMEOUT_SECONDS
            )

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response

    @classmethod
    def update_user(cls, form_data, id):

        form_data['birthdate'] = form_data['birthdate'].strftime("%d/%m/%Y")

        if "profile_picture" in form_data.keys():
            file = form_data["profile_picture"]
            name = file.filename
            name = str(uuid4()) + secure_filename(name)

            path = os.path.join(current_app.config["UPLOAD_FOLDER"], name)
            form_data['profile_picture'] = name
            print('PIPPO', os.listdir('/static/assets'))
            file.save(path)
        else:
            form_data['profile_picture'] = "default.png"

        try:
            url = "%s/user/%s" % (cls.USERS_ENDPOINT, str(id))
            response = requests.put(url,
                                    json=form_data,
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                    )

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response

    @classmethod
    def delete_user(cls, user_id: int):
        """
        This method contacts the users microservice
        to delete the account of the user
        :param user_id: the user id
        :return: User updated
        """
        try:
            logout_user()
            url = "%s/user/%s" % (cls.USERS_ENDPOINT, str(user_id))
            response = requests.delete(url, timeout=cls.REQUESTS_TIMEOUT_SECONDS)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response

    @classmethod
    def _content_filter(cls, user_id: int) : 

        try:
            url = "%s/content_filter/%s" % (cls.USERS_ENDPOINT, str(user_id))
            response = requests.get(url,timeout=cls.REQUESTS_TIMEOUT_SECONDS)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response
        

    @classmethod
    def authenticate_user(cls, email: str, password: str) -> User:
        """
        This method authenticates the user trough users AP
        :param email: user email
        :param password: user password
        :return: None if credentials are not correct, User instance if credentials are correct.
        """
        payload = dict(email=email, password=password)
        try:
            print('trying response....')
            response = requests.post('%s/authenticate' % cls.USERS_ENDPOINT,
                                     json=payload,
                                     timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                     )
            print('received response....')
            json_response = response.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # We can't connect to Users MS
            return abort(500)

        if response.status_code == 401:
            # user is not authenticated
            return None
        elif response.status_code == 200:
            user = User.build_from_json(json_response['user'])
            return user
        else:
            raise RuntimeError(
                'Microservice users returned an invalid status code %s, and message %s'
                % (response.status_code, json_response['error_message'])
            )

    @classmethod
    def add_to_blacklist(cls, other_id: int) -> Tuple[int, str]:
        endpoint = f"{cls.USERS_ENDPOINT}/blacklist/{current_user.id}/{other_id}"
        try:
            response = requests.put(endpoint, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            message = response.json()['message']

            return response.status_code, message

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, 'unexpected error'

    @classmethod
    def remove_from_blacklist(cls, other_id: int) -> Tuple[int, str]:
        endpoint = f"{cls.USERS_ENDPOINT}/blacklist/{current_user.id}/{other_id}"
        try:
            response = requests.delete(endpoint, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            message = response.json()['message']

            return response.status_code, message

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, 'unexpected error'

    @classmethod
    def report_user(cls, other_id: int) -> Tuple[int, str]:
        endpoint = f"{cls.USERS_ENDPOINT}/report/{current_user.id}/{other_id}"
        try:
            response = requests.put(endpoint, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            message = response.json()['message']

            return response.status_code, message

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, 'unexpected error'

    @classmethod
    def get_user_status(cls, other_id: int) -> Tuple[bool, bool]:
        endpoint = f"{cls.USERS_ENDPOINT}/user_status/{current_user.id}/{other_id}"
        try:

            response = requests.get(endpoint, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            json_pl = response.json()
            return json_pl['blocked'], json_pl['reported']

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return False



