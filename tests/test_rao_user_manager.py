import mock
import pytest
import requests
from werkzeug.exceptions import InternalServerError

from mib.rao.user_manager import UserManager

class MockRespose:
    def __init__(self, code=200, json={}):
        self.status_code = code
        self.json_data = json

    def json(self):
        return self.json_data


class TestUserManager:

    @pytest.mark.parametrize("users, propics, code, bl",[
        (['u1', 'u2'], ['p1', 'p2'], 200, False),
        (['u1', 'u2'], ['p1', 'p2'], 200, True),
        ([], [], 404, False),
        ([], [], 404, True),
    ])
    def test_get_user_list(self, mock_get, mock_user_bfj, users, propics, code, bl):
        mock_get.return_value = MockRespose(
            code=code, 
            json={ 'users': users, 'profile_pictures': propics, }
        )
        _users, _propics, _code = UserManager.get_users_list(1, '', bl)
        assert _users == users
        assert _propics == propics
        assert _code == code

    @pytest.mark.parametrize("exception, bl",[
        (requests.exceptions.ConnectionError, True),
        (requests.exceptions.ConnectionError, False),
        (requests.exceptions.Timeout, True),
        (requests.exceptions.Timeout, False),
    ])
    def test_get_user_list_error(self, mock_get, exception, bl):
        mock_get.reset_mock(side_effect=True)
        mock_get.side_effect = exception()

        _users, _propics, _code = UserManager.get_users_list(1, '', bl)
        assert _users == []
        assert _propics == []
        assert _code == 500

    @pytest.mark.parametrize("user, propic, code, cache",[
        ('u1', 'p1', 200, False),
        ('u1', 'p1', 200, True),
        (None, '', 404, False),
    ])
    def test_get_user_by_id(self, mock_get, mock_user_bfj, user, propic, code, cache):
        mock_get.reset_mock(side_effect=True)
        mock_get.return_value = MockRespose(
            code=code, 
            json={ 'user': user, 'profile_picture': propic, }
        )
        with mock.patch('mib.rao.utils.Utils.save_profile_picture'):
            _user, _propic = UserManager.get_user_by_id(1, cache_propic=cache)
            assert _user == user
            assert _propic == propic

    def test_get_user_by_id_unexptected(self, mock_get, mock_user_bfj):
        mock_get.reset_mock(side_effect=True)
        mock_get.return_value = MockRespose(
            code=403, 
            json={ 'user': None, 'profile_picture': '', }
        )

        with pytest.raises(RuntimeError):
            UserManager.get_user_by_id(1)

    @pytest.mark.parametrize("exception",[
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    ])
    def test_get_user_by_id_error(self, mock_get, mock_user_bfj, exception):
        mock_get.reset_mock(side_effect=True)
        mock_get.side_effect = exception()

        with pytest.raises(InternalServerError):
            UserManager.get_user_by_id(1)





