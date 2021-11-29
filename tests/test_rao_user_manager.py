import io
import mock
from datetime import datetime
import pytest
import requests
from werkzeug.exceptions import InternalServerError
from werkzeug.datastructures import FileStorage
from testing.fake_response import MockResponse
from mib.rao.user_manager import UserManager

test_user_create = {
    'first_name': 'Jack',
    'last_name': 'Black',
    'nickname': '_jackblack_',
    'email': 'jack.black@example.com',
    'password': 'admin',
    'birthdate': datetime.strptime('01/01/1990', '%d/%m/%Y'),
    'location': 'collesalvetti',
}

test_user_update = test_user_create.copy()
del test_user_update['password']
test_user_update['old_password'] = 'admin'
test_user_update['new_password'] = 'admin1'

class TestUserManager:

    @pytest.mark.parametrize("users, propics, code, bl",[
        (['u1', 'u2'], ['p1', 'p2'], 200, False),
        (['u1', 'u2'], ['p1', 'p2'], 200, True),
        ([], [], 404, False),
        ([], [], 404, True),
    ])
    def test_get_user_list(self, mock_get, mock_user_bfj, users, propics, code, bl):
        mock_get.return_value = MockResponse(
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

    @pytest.mark.parametrize("function, par, user, propic, code, cache",[
        (UserManager.get_user_by_id, 1, 'u1', 'p1', 200, False),
        (UserManager.get_user_by_id, 1, 'u1', 'p1', 200, True),
        (UserManager.get_user_by_id, 1, None, '', 404, False),
        (UserManager.get_user_by_email, "email@email.com", 'u1', 'p1', 200, False),
        (UserManager.get_user_by_email, "email@email.com", 'u1', 'p1', 200, True),
        (UserManager.get_user_by_email, "email@email.com", None, '', 404, False),
        (UserManager.get_user_by_phone, "0000000000", 'u1', 'p1', 200, False),
        (UserManager.get_user_by_phone, "0000000000", 'u1', 'p1', 200, True),
        (UserManager.get_user_by_phone, "0000000000", None, '', 404, False),
    ])
    def test_get_user_by(self, mock_get, mock_user_bfj, function, par, user, propic, code, cache):
        mock_get.reset_mock(side_effect=True)
        mock_get.return_value = MockResponse(
            code=code, 
            json={ 'user': user, 'profile_picture': propic, }
        )
        with mock.patch('mib.rao.utils.Utils.save_profile_picture'):
            _user, _propic = function(par, cache_propic=cache)
            assert _user == user
            assert _propic == propic

    @pytest.mark.parametrize("function, par",[
        (UserManager.get_user_by_id, 1),
        (UserManager.get_user_by_email, "email@email.com"),
        (UserManager.get_user_by_phone, "0000000000"),
    ])
    def test_get_user_by_id_unexptected(self, mock_get, mock_user_bfj, function, par):
        mock_get.reset_mock(side_effect=True)
        mock_get.return_value = MockResponse(
            code=403, 
            json={ 'user': None, 'profile_picture': '', }
        )
        with pytest.raises(RuntimeError):
            function(par)

    @pytest.mark.parametrize("function, par, exception",[
        (UserManager.get_user_by_id, 1, requests.exceptions.ConnectionError),
        (UserManager.get_user_by_id, 1,requests.exceptions.Timeout),
        (UserManager.get_user_by_email, "email@email.com", requests.exceptions.ConnectionError),
        (UserManager.get_user_by_email, "email@email.com", requests.exceptions.Timeout),
        (UserManager.get_user_by_phone, "0000000000",requests.exceptions.ConnectionError),
        (UserManager.get_user_by_phone, "0000000000",requests.exceptions.Timeout),
    ])
    def test_get_user_by_id_error(self, mock_get, mock_user_bfj, function, par, exception):
        mock_get.reset_mock(side_effect=True)
        mock_get.side_effect = exception()
        with pytest.raises(InternalServerError):
            function(par)

    @pytest.mark.parametrize("data, propic, code, message",[
        (test_user_create.copy(), True, 201, 'user created'),
        (test_user_create.copy(), True, 200, 'user existing'),
        (test_user_create.copy(), False, 201, 'user created'),
    ])
    def test_create_user(self, mock_post, data, propic, code, message):
        mock_post.reset_mock(side_effect=True)
        mock_post.return_value = MockRespose(
            code=code, 
            json={ 'user': data, 'profile_picture': '', 'message': message}
        )
        with mock.patch('mib.rao.utils.Utils.save_profile_picture'):
            with mock.patch.object(FileStorage, "save", autospec=True, return_value=None):
                image_name = "test.png"
                file = FileStorage(filename=image_name, stream=io.BytesIO(b"data data"))
                if propic:
                    data['profile_picture'] = file
                _code, _message, _user = UserManager.create_user(data)
                assert _code == code
                assert _message == message
                if code == 201:
                    for k in data.keys():
                        assert _user[k] == data[k]
                else:
                    assert _user == None

    @pytest.mark.parametrize("exception",[
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    ])
    def test_create_user_error(self, mock_post, exception):
        mock_post.reset_mock(side_effect=True)
        mock_post.side_effect = exception()
        code, message, user =  UserManager.create_user({'birthdate': datetime.strptime('01/01/2021', '%d/%m/%Y')})
        assert code == 500
        assert message == "Unexpected result from user microservice"
        assert user == None
        
    @pytest.mark.parametrize("data, propic, code, message",[
        (test_user_update.copy(), True, 201, 'user created'),
        (test_user_update.copy(), True, 404, 'user not found'),
        (test_user_update.copy(), True, 400, 'email used'),
        (test_user_update.copy(), True, 400, 'phone used'),
        (test_user_update.copy(), True, 200, 'password incorrect'),
        (test_user_update.copy(), False, 201, 'user created'),
    ])
    def test_update_user(self, mock_put, data, propic, code, message):
        mock_put.reset_mock(side_effect=True)
        mock_put.return_value = MockRespose(
            code=code, 
            json={ 'user': data, 'profile_picture': '', 'message': message}
        )
        with mock.patch('mib.rao.utils.Utils.save_profile_picture'):
            with mock.patch.object(FileStorage, "save", autospec=True, return_value=None):
                image_name = "test.png"
                file = FileStorage(filename=image_name, stream=io.BytesIO(b"data data"))
                if propic:
                    data['profile_picture'] = file
                _code, _message = UserManager.update_user(data, 1)
                assert _code == code
                assert _message == message

    @pytest.mark.parametrize("exception",[
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    ])
    def test_update_user_error(self, mock_put, exception):
        mock_put.reset_mock(side_effect=True)
        mock_put.side_effect = exception()
        code, message =  UserManager.update_user({'birthdate': datetime.strptime('01/01/2021', '%d/%m/%Y')}, 1)
        assert code == 500
        assert message == "Unexpected response from user microservice"

    '''
    @pytest.mark.parametrize("code, message",[
        (202, 'user deleted'),
        (404, 'user not found')
    ])
    def test_delete_user(self, mock_del, code, message):
        with mock.patch('flask_login.utils.logout_user', return_value=True):
            mock_del.reset_mock(side_effect=True)
            mock_del.return_value = MockRespose(
                code=code, 
                json={ 'message': message }
            )
            response = UserManager.delete_user(1)
            assert response == mock_del.return_value
    '''

    @pytest.mark.parametrize("code, message",[
        (200, 'content filter toggled'),
        (404, 'user not found')
    ])
    def test_content_filter(self, mock_get, code, message):
        mock_get.reset_mock(side_effect=True)
        mock_get.return_value = MockRespose(
            code=code, 
            json={ 'message': message }
        )
        response = UserManager.toggle_content_filter(1)
        assert response == mock_get.return_value
        
    @pytest.mark.parametrize("exception",[
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    ])
    def test_content_filter_error(self, mock_get, exception):
        mock_get.reset_mock(side_effect=True)
        mock_get.side_effect = exception()
        with pytest.raises(InternalServerError):
            UserManager.toggle_content_filter(1)

    @pytest.mark.parametrize("args, code, user",[
        (('email@email.com', 'pw'), 200, 'u1'),
        (('email@email.com', 'pw'), 401, None),
        (('email@email.com', 'pw'), 404, None),
    ])
    def test_authenticate_user(self, mock_post, args, code, user):
        mock_post.reset_mock(side_effect=True)
        mock_post.return_value = MockRespose(
            code=code, 
            json={ 'user': user, 'profile_picture': '', 'error_message': '' }
        )
        with mock.patch('mib.rao.utils.Utils.save_profile_picture'):
            if code in [200, 401]:
                _user = UserManager.authenticate_user(*args)
                assert _user == user
            else:
                with pytest.raises(RuntimeError):
                    UserManager.authenticate_user(*args)
        
    @pytest.mark.parametrize("exception",[
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    ])
    def test_authenticate_user_error(self, mock_post, exception):
        mock_post.reset_mock(side_effect=True)
        mock_post.side_effect = exception()
        with pytest.raises(InternalServerError):
            UserManager.authenticate_user(None, None)

    @pytest.mark.parametrize("args, code, message",[
        ((1, 2), 201, 'user added'),
        ((1, 2), 200, 'user already in blacklist'),
        ((1, 1), 403, 'cannot block self'),
        ((1, 3), 404, 'user not found'),
    ])
    def test_blacklist_add(self, mock_put, args, code, message):
        mock_put.reset_mock(side_effect=True)
        mock_put.return_value = MockRespose(
            code=code, 
            json={ 'message': message }
        )
        _code, _message = UserManager.add_to_blacklist(*args)
        assert _code == code
        assert _message == message
        
    @pytest.mark.parametrize("exception",[
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    ])
    def test_blacklist_add_error(self, mock_put, exception):
        mock_put.reset_mock(side_effect=True)
        mock_put.side_effect = exception()
        _code, _message = UserManager.add_to_blacklist(1, 2)
        assert _code == 500
        assert _message == 'unexpected error'

    @pytest.mark.parametrize("args, code, message",[
        ((1, 2), 200, 'user removed'),
        ((1, 3), 404, 'user not found'),
    ])
    def test_blacklist_remove(self, mock_del, args, code, message):
        mock_del.reset_mock(side_effect=True)
        mock_del.return_value = MockRespose(
            code=code, 
            json={ 'message': message }
        )
        _code, _message = UserManager.remove_from_blacklist(*args)
        assert _code == code
        assert _message == message
        
    @pytest.mark.parametrize("exception",[
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    ])
    def test_blacklist_remove_error(self, mock_del, exception):
        mock_del.reset_mock(side_effect=True)
        mock_del.side_effect = exception()
        _code, _message = UserManager.remove_from_blacklist(1, 2)
        assert _code == 500
        assert _message == 'unexpected error'

    @pytest.mark.parametrize("args, code, message",[
        ((1, 2), 201, 'user reported'),
        ((1, 2), 200, 'user already reported'),
        ((1, 1), 403, 'cannot report self'),
        ((1, 3), 404, 'user not found'),
    ])
    def test_report_user(self, mock_put, args, code, message):
        mock_put.reset_mock(side_effect=True)
        mock_put.return_value = MockRespose(
            code=code, 
            json={ 'message': message }
        )
        _code, _message = UserManager.report_user(*args)
        assert _code == code
        assert _message == message
        
    @pytest.mark.parametrize("exception",[
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    ])
    def test_report_user_error(self, mock_put, exception):
        mock_put.reset_mock(side_effect=True)
        mock_put.side_effect = exception()
        _code, _message = UserManager.report_user(1, 2)
        assert _code == 500
        assert _message == 'unexpected error'

    @pytest.mark.parametrize("reported, blocked",[
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ])
    def test_user_status(self, mock_get, reported, blocked):
        mock_get.reset_mock(side_effect=True)
        mock_get.return_value = MockRespose(
            code=200, 
            json={ 'reported': reported, 'blocked': blocked }
        )
        _blocked, _reported = UserManager.get_user_status(1, 2)
        assert _blocked == blocked
        assert _reported == reported
        
    @pytest.mark.parametrize("exception",[
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    ])
    def test_user_status_error(self, mock_get, exception):
        mock_get.reset_mock(side_effect=True)
        mock_get.side_effect = exception()
        _blocked, _reported = UserManager.get_user_status(1, 2)
        assert _blocked == False
        assert _reported == False

