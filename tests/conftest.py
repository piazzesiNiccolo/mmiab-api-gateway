import pytest
import mock
from mib import create_app

@pytest.fixture(scope="session", autouse=False)
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


