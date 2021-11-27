import pytest
import responses
from mib import create_app

@pytest.fixture(scope="session", autouse=True)
def test_client():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    with app.test_client() as client:
        yield client


