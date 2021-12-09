import base64
from mib.auth.user import User
from flask_login import logout_user
from flask_login import current_user
from flask import abort
from flask import current_app as app
import requests
from typing import List
from typing import Tuple
from mib.rao.utils import Utils

class UserManager:
    
    @classmethod
    def users_endpoint(cls):
        return app.config['USERS_MS_URL']
    
    @classmethod
    def requests_timeout_seconds(cls):
        return app.config['REQUESTS_TIMEOUT_SECONDS']
    
    @classmethod
    def get_users_list(cls, id: int, query: str, blacklist: bool = False) -> Tuple[List[User], int]:

        target = "blacklist" if blacklist else "users_list"
        endpoint = f"{cls.users_endpoint()}/{target}/{id}?q={query}"

        try:
            response = requests.get(endpoint, timeout=cls.requests_timeout_seconds())

            users = [ User.build_from_json(u) for u in response.json()['users'] ]
            propics = response.json()['profile_pictures']
            return users, propics, response.status_code

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return [], [], 500

    @classmethod
    def get_user_by_id(cls, user_id: int, cache_propic=False) -> User:
        """
        This method contacts the users microservice
        and retrieves the user object by user id.
        :param user_id: the user id
        :return: User obj with id=user_id
        """
        try:
            response = requests.get("%s/user/%s" % (cls.users_endpoint(), str(user_id)),
                                    timeout=cls.requests_timeout_seconds())
            json_payload = response.json()
            if response.status_code == 200:
                # user is authenticated
                user = User.build_from_json(json_payload['user'])
                propic = json_payload['profile_picture'] 
                if cache_propic:
                    Utils.save_profile_picture(propic)
            elif response.status_code == 404:
                user, propic = None, ''
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return user, propic

    @classmethod
    def get_user_by_email(cls, user_email: str, cache_propic=False):
        """
        This method contacts the users microservice
        and retrieves the user object by user email.
        :param user_email: the user email
        :return: User obj with email=user_email
        """
        try:
            response = requests.get("%s/user_email/%s" % (cls.users_endpoint(), user_email),
                                    timeout=cls.requests_timeout_seconds())
            json_payload = response.json()
            user, propic = None, ''

            if response.status_code == 200:
                user = User.build_from_json(json_payload['user'])
                propic = json_payload['profile_picture'] 
                if cache_propic:
                    Utils.save_profile_picture(propic)
            elif response.status_code == 404:
                user, propic = None, ''
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return user, propic

    @classmethod
    def get_user_by_phone(cls, user_phone: str, cache_propic=False) -> User:
        """
        This method contacts the users microservice
        and retrieves the user object by user phone.
        :param user_phone: the user phone
        :return: User obj with phone=user_phone
        """
        try:
            response = requests.get("%s/user_phone/%s" % (cls.users_endpoint(), user_phone),
                                    timeout=cls.requests_timeout_seconds())
            json_payload = response.json()
            user, propic = None, ''

            if response.status_code == 200:
                user = User.build_from_json(json_payload['user'])
                propic = json_payload['profile_picture'] 
                if cache_propic:
                    Utils.save_profile_picture(propic)
            elif response.status_code == 404:
                user, propic = None, ''
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return user, propic

    @classmethod
    def create_user( cls, form_data ) -> Tuple[int, str, User]:
        form_data['birthdate'] = form_data['birthdate'].strftime("%d/%m/%Y")

        if "profile_picture" in form_data.keys():
            file = form_data["profile_picture"]
            b64_file = base64.b64encode(file.read()).decode("utf8")

            form_data['profile_picture'] = {
                'name': file.filename,
                'data': b64_file,
            }
        else:
            form_data['profile_picture'] = ''

        try:
            url = "%s/user" % cls.users_endpoint()
            response = requests.post(
                url,
                json=form_data,
                timeout=cls.requests_timeout_seconds()
            )
            code = response.status_code
            json_pl = response.json()
            user = None
            message = json_pl['message']
            if code == 201:
                user = json_pl['user']
                Utils.save_profile_picture(json_pl['profile_picture'])

            return code, message, user

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected result from user microservice", None


    @classmethod
    def update_user(cls, form_data, id) -> Tuple[int, str]:

        form_data['birthdate'] = form_data['birthdate'].strftime("%d/%m/%Y")

        if "profile_picture" in form_data.keys():
            file = form_data["profile_picture"]
            b64_file = base64.b64encode(file.read()).decode("utf8")

            form_data['profile_picture'] = {
                'name': file.filename,
                'data': b64_file,
            }

        try:
            url = "%s/user/%s" % (cls.users_endpoint(), str(id))
            response = requests.put(url,
                                    json=form_data,
                                    timeout=cls.requests_timeout_seconds()
                                    )
            code = response.status_code
            message = response.json()['message']
            if code == 201:
                Utils.save_profile_picture(response.json()['profile_picture'])
            return code, message

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected response from user microservice"


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
            url = "%s/user/%s" % (cls.users_endpoint(), str(user_id))
            response = requests.delete(url, timeout=cls.requests_timeout_seconds())

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
              return 500, "Unexpected response from user microservice"

        return response

    @classmethod
    def toggle_content_filter(cls, user_id: int) : 

        try:
            url = "%s/content_filter/%s" % (cls.users_endpoint(), str(user_id))
            response = requests.get(url,timeout=cls.requests_timeout_seconds())

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
            response = requests.post('%s/authenticate' % cls.users_endpoint(),
                                     json=payload,
                                     timeout=cls.requests_timeout_seconds()
                                     )
            json_response = response.json()

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # We can't connect to Users MS
            return abort(500)

        if response.status_code == 401:
            # user is not authenticated
            return None
        elif response.status_code == 200:
            Utils.save_profile_picture(json_response['profile_picture'])
            user = User.build_from_json(json_response['user'])
            return user
        else:
            raise RuntimeError(
                'Microservice users returned an invalid status code %s, and message %s'
                % (response.status_code, json_response['error_message'])
            )

    @classmethod
    def add_to_blacklist(cls, user_id: int, other_id: int) -> Tuple[int, str]:
        endpoint = f"{cls.users_endpoint()}/blacklist/{user_id}/{other_id}"
        try:
            response = requests.put(endpoint, timeout=cls.requests_timeout_seconds())
            message = response.json()['message']

            return response.status_code, message

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, 'unexpected error'

    @classmethod
    def remove_from_blacklist(cls, user_id: int, other_id: int) -> Tuple[int, str]:
        endpoint = f"{cls.users_endpoint()}/blacklist/{user_id}/{other_id}"
        try:
            response = requests.delete(endpoint, timeout=cls.requests_timeout_seconds())
            message = response.json()['message']

            return response.status_code, message

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, 'unexpected error'

    @classmethod
    def report_user(cls, user_id: int, other_id: int) -> Tuple[int, str]:
        endpoint = f"{cls.users_endpoint()}/report/{user_id}/{other_id}"
        try:
            response = requests.put(endpoint, timeout=cls.requests_timeout_seconds())
            message = response.json()['message']

            return response.status_code, message

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, 'unexpected error'

    @classmethod
    def get_user_status(cls, user_id: int, other_id: int) -> Tuple[bool, bool]:
        endpoint = f"{cls.users_endpoint()}/user_status/{user_id}/{other_id}"
        try:

            response = requests.get(endpoint, timeout=cls.requests_timeout_seconds())
            json_pl = response.json()
            return json_pl['blocked'], json_pl['reported']

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return False, False

    @classmethod
    def get_recipients(cls, user_id, query: str = None):
        qstr = f'?q={query}' if query is not None else ''
        endpoint = f"{cls.users_endpoint()}/recipients/{user_id}{qstr}"

        try:
            response = requests.get(endpoint, timeout=cls.requests_timeout_seconds())
            json = response.json()
            if response.status_code == 200:
                return [(item["id"],item["nickname"] if item["nickname"] else item["email"]) for item in json["users"]]

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return []

        return []



