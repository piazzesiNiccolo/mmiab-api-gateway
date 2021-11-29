import flask_login
import pytest
import mock
from mib import create_app
from mib.auth.user import User
@pytest.fixture(scope="session", autouse=True)
def test_client():
    app = create_app()
    with app.app_context():
        with app.test_client() as client:
            yield client

@pytest.fixture(scope='session')
def mock_get():
    with mock.patch('requests.get') as _mock:
        yield _mock

@pytest.fixture(scope='session')
def mock_user_bfj():
    with mock.patch('mib.auth.user.User.build_from_json', new=lambda e: e) as _mock:
        yield _mock

@pytest.fixture
def mock_current_user():
    with mock.patch("flask_login.utils._get_user") as m:
        mock_current_user.return_value = User(id=1, email="email@email.com", is_active=True, authenticated=True, is_anonymous=False,extra='')
        yield m

