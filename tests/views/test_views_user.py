from flask.helpers import get_flashed_messages
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

    @pytest.mark.parametrize(
        "code, message",
        [
            (200, "A user with this email is already registered"),
            (201, "User succesfully registered"),
            (500, "Unexpected response from users microservice!"),
        ],
    )
    def test_create_user_valid_form(
        self, test_client, mock_cu, mock_user_bfj, code, message
    ):
        data = {
            "first_name": "Niccolò",
            "last_name": "Piazzesi",
            "email": "email@email.com",
            "birthdate": "1998-02-19",
            "password": "Password12",
            "phone": "1234567890",
            "nickname": "npiazzesi",
            "is_active": False,
        }

        mock_cu.return_value = (
            code,
            message,
            User(
                id=1,
                email=data["email"],
                is_active=False,
                authenticated=False,
                is_anonymous=False,
                extra="",
            ),
        )
        resp = test_client.post("/create_user", data=data, follow_redirects=True)
        assert message in flask.get_flashed_messages()
        assert resp.status_code == 200
        assert b"Message in a Bottle" in resp.data

    @pytest.mark.parametrize(
        "code, message",
        [
            (
                202,
                b"Message in a Bottle",
            ),
            (500, b"Delete Account"),
        ],
    )
    def test_delete_user(self, test_client, mock_current_user, code, message):
        with mock.patch("mib.rao.user_manager.UserManager.delete_user") as m:
            m.return_value = MockResponse(code=code)
            resp = test_client.get("/delete_user/1")
            assert resp.status_code == 302

    @pytest.mark.parametrize(
        "code, message",
        [
            (404, "Error to set content filter"),
            (200, "Content filter value successfully changed!"),
        ],
    )
    def test_content_filter(self, test_client, code, message, mock_current_user):
        with mock.patch("mib.rao.user_manager.UserManager.toggle_content_filter") as m:
            m.return_value = MockResponse(code=code, json={})
            resp = test_client.get("/content_filter")
            assert message in flask.get_flashed_messages()
            assert resp.status_code == 302

    @pytest.mark.parametrize(
        "code, message",
        [
            (404, "User not found"),
            (500, "Unexpected response from users microservice!"),
        ],
    )
    def test_user_list_error(self, test_client, mock_current_user, code, message):
        with mock.patch("mib.rao.user_manager.UserManager.get_users_list") as m:
            m.return_value = None, None, code
            resp = test_client.get("/users?q=keyword")
            assert message in get_flashed_messages()
            assert resp.status_code == 302

    def test_user_list(self, test_client, mock_current_user):
        with mock.patch("mib.rao.user_manager.UserManager.get_users_list") as m:
            m.return_value = [], [], 200
            resp = test_client.get("/users?q=keyword")
            assert resp.status_code == 200
            assert b"Users" in resp.data

    def test_user_info_not_exists(self, test_client, mock_current_user):
        with mock.patch("mib.rao.user_manager.UserManager.get_user_by_id") as m:
            m.return_value = None, None
            resp = test_client.get("/user/1")
            assert "User not found!" in get_flashed_messages()
            assert resp.status_code == 302

    @pytest.mark.parametrize("blocked", [True, False])
    @pytest.mark.parametrize("reported", [True, False])
    def test_user_info_ok(self, test_client, mock_current_user, blocked, reported):
        with mock.patch("mib.rao.user_manager.UserManager.get_user_by_id") as m:
            m.return_value = (
                User(
                    id=1,
                    email="email@email.com",
                    is_active=True,
                    authenticated=True,
                    is_anonymous=False,
                    extra="",
                ),
                None,
            )
            with mock.patch("mib.rao.user_manager.UserManager.get_user_status") as m2:
                m2.return_value = blocked, reported
                resp = test_client.get("/user/1")
                assert resp.status_code == 200
                blocked_data = b"Unblock" if blocked else b"Block"
                assert blocked_data in resp.data
                if not reported:
                    assert b"Report" in resp.data

    def test_get_current_user_profile(self, test_client, mock_current_user):
        resp = test_client.get("/profile")
        assert resp.status_code == 302

    def test_edit_user_page(self, test_client, mock_current_user):
        with mock.patch("mib.rao.user_manager.UserManager.get_user_by_id") as m:
            m.return_value = (
                User(
                    id=1,
                    email="email@email.com",
                    is_active=True,
                    authenticated=True,
                    is_anonymous=False,
                    extra={"birthdate": "19/02/1998"},
                ),
                None,
            )
            resp = test_client.get("/profile/edit")
            assert resp.status_code == 200
            assert b"submit" in resp.data

    @pytest.mark.parametrize(
        "code, message",
        [
            (200, "Password incorrect"),
            (201, "User profile successfully updated"),
            (404, "User not found"),
            (400, "Phone already used"),
            (400, "Email already used"),
            (500, "Unexpected response from users microservice!"),
        ],
    )
    def test_edit_user_valid_form(self, test_client, mock_current_user, code, message):
        data = {
            "first_name": "Niccolò",
            "last_name": "Piazzesi",
            "email": "email@email.com",
            "birthdate": "1998-02-19",
            "password": "Password12",
            "phone": "1234567890",
            "nickname": "npiazzesi",
            "is_active": False,
        }

        with mock.patch("mib.rao.user_manager.UserManager.update_user") as m:
            m.return_value = (code, message)
            resp = test_client.post("/profile/edit", data=data)
            assert message in flask.get_flashed_messages()
            assert resp.status_code == 302

    def test_user_blacklist_ok(self, test_client, mock_current_user):
        with mock.patch("mib.rao.user_manager.UserManager.get_users_list") as m:
            m.return_value = [], [], 200
            resp = test_client.get("/blacklist")
            assert resp.status_code == 200
            assert b"Users" in resp.data

    @pytest.mark.parametrize(
        "code, message",
        [
            (404, "User not found"),
            (500, "Unexpected response from users microservice!"),
        ],
    )
    def test_user_blacklist_error(self, test_client, mock_current_user, code, message):
        with mock.patch("mib.rao.user_manager.UserManager.get_users_list") as m:
            m.return_value = None, None, code
            resp = test_client.get("/blacklist?q=keyword")
            assert message in get_flashed_messages()
            assert resp.status_code == 302

    @pytest.mark.parametrize(
        "code, message",
        [
            (200, "User removed blacklist"),
            (404, "Blocking user not found"),
            (404, "Blocked user not found"),
            (500, "Unexpected response from users microservice!"),
        ],
    )
    def test_user_add_to_blacklist(self, test_client, mock_current_user, code, message):
        with mock.patch("mib.rao.user_manager.UserManager.remove_from_blacklist") as m:
            m.return_value = code, message
            resp = test_client.get("/blacklist/1/remove")
            assert resp.status_code == 302
            assert message in flask.get_flashed_messages()

    @pytest.mark.parametrize(
        "code, message",
        [
            (201, "User added to blacklist"),
            (200, "User already in blacklist"),
            (404, "Blocking user not found"),
            (404, "Blocked user not found"),
            (403, "Users cannot block themselves"),
            (500, "Unexpected response from users microservice!"),
        ],
    )
    def test_user_remove_from_blacklist(
        self, test_client, mock_current_user, code, message
    ):
        with mock.patch("mib.rao.user_manager.UserManager.add_to_blacklist") as m:
            m.return_value = code, message
            resp = test_client.get("/blacklist/1/add")
            assert resp.status_code == 302
            assert message in flask.get_flashed_messages()

    @pytest.mark.parametrize(
        "code, message",
        [
            (403, "Users cannot report themselves"),
            (404, "Reported user not found"),
            (404, "User not found"),
            (200, "You have already reported this user"),
            (201, "User succesfully reported"),
            (500, "Unexpected response from users microservice!"),
        ],
    )
    def test_report(self, test_client, mock_current_user, code, message):
        with mock.patch("mib.rao.user_manager.UserManager.report_user") as m:
            m.return_value = code, message
            resp = test_client.get("/report/1")
            assert message in get_flashed_messages()
            assert resp.status_code == 302
