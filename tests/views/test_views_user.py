from _pytest.fixtures import pytest_fixture_setup
import pytest
import datetime
import mock
import flask
from flask_login import current_user
from mib.auth.user import User
from testing.fake_response import MockResponse
@pytest.fixture
def mock_cu():
    with mock.patch("mib.rao.user_manager.UserManager.create_user") as m:
        yield m


class TestViewsUsers:

    def test_get_create_user_page(self, test_client):
        resp = test_client.get("/create_user/")
        assert resp.status_code == 200
        assert b"submit" in resp.data
    
    @pytest.mark.parametrize("code, message",[ 
        (200,"A user with this email is already registered"),
        (201, "User succesfully registered"),
        (500, "Unexpected response from users microservice!")
    ])
    def test_create_user_valid_form(self, test_client, mock_cu,mock_user_bfj, code, message):
        data = {
            "first_name" : "Niccolò",
            "last_name" :"Piazzesi",
            "email":"email@email.com",
            "birthdate" : "19/02/1998",
            "password" : "Password12",
            "phone" : "1234567890",
            "nickname" : "npiazzesi",
            "is_active":False
        }
        
        mock_cu.return_value  = code, message, User(id=1, email=data["email"], is_active=False, authenticated=False, is_anonymous=False,extra='')
        resp = test_client.post("/create_user", data=data,follow_redirects=True)
        assert message  in  flask.get_flashed_messages()
        assert resp.status_code == 200
        assert b"Message in a Bottle" in resp.data
    
    @pytest.mark.parametrize("code, message",[ 
        (202,b"Message in a Bottle",),
        (500,b"Delete Account")
    ])
    def test_delete_user(self, test_client,mock_current_user, code, message):
        with mock.patch("mib.rao.user_manager.UserManager.delete_user") as m:
            m.return_value = MockResponse(code=code)
            resp = test_client.get("/delete_user/1")
            assert resp.status_code == 302

    @pytest.mark.parametrize("code, message",[
        (404, "Error to set content filter"),
        (200, "Content filter value successfully changed!")
    ])
    def test_content_filter(self, test_client,code,message, mock_current_user):
        with mock.patch("mib.rao.user_manager.UserManager.toggle_content_filter") as m:
            m.return_value = MockResponse(code=code, json={})
            resp = test_client.get("/content_filter")
            assert message in flask.get_flashed_messages()
            assert resp.status_code == 302
