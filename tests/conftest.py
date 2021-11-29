import pytest
import mock
from mib import create_app

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
def mock_post():
    with mock.patch('requests.post') as _mock:
        yield _mock

@pytest.fixture(scope='session')
def mock_put():
    with mock.patch('requests.put') as _mock:
        yield _mock

@pytest.fixture(scope='session')
def mock_del():
    with mock.patch('requests.delete') as _mock:
        yield _mock

@pytest.fixture(scope='session')
def mock_user_bfj():
    with mock.patch('mib.auth.user.User.build_from_json', new=lambda e: e) as _mock:
        yield _mock


