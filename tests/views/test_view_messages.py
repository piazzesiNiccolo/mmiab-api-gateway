import pytest

class TestViewMessages:

    def test_post_draft(self, test_client):

        data = {
                    "id_sender" : 1,
                    "body_message": "hello world",
                    "date_of_send": "10:05 07/07/2022",
                    "recipients-0-recipient": "2",
                }
        response = test_client.post("/draft", data=data, follow_redirects=True)
        assert response.status_code == 200