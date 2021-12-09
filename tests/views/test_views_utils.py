import pytest
class TestViewsUtils:

    def test_generate_error(self,test_client):
        resp = test_client.get("/server_error") 
        assert resp.status_code == 302