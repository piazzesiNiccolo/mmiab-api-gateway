

class TestViewsHome:

    def test_home_no_auth(self, test_client):
        response = test_client.get('/')
        assert response.status_code == 200

    def test_home_auth(self, test_client, mock_current_user):
        response = test_client.get('/')
        assert response.status_code == 302


