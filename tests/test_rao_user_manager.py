import pytest
import requests
from requests.api import request
import responses
from mib.rao.user_manager import UserManager
class TestUserManager:

    @responses.activate
    def test_get_user_list(self, mock_resps: responses.RequestsMock):
        endpoint = f"{UserManager.USERS_ENDPOINT}/users_lists/1?q="
        mock_resps.add(responses.GET,endpoint,json={
            "users": [
                {
                    "first_name":"Name",
                    "last_name": "Surname",
                    "email":"email@email.com",
                    "birthdate":"01/01/2000"
                },

                {
                    "first_name":"Name2",
                    "last_name": "Surname2",
                    "email":"email1@email1.com",
                    "birthdate":"01/01/20001"
                },

                {
                    "first_name":"Name3",
                    "last_name": "Surname3",
                    "email":"email2@email2.com",
                    "birthdate":"01/01/2002"
                }
            ]
        }, status=200)
        resp = requests.get(endpoint)
        assert len(resp.json["users"]) == 3
        assert resp.status_code == 200
        assert len(responses.calls) == 1