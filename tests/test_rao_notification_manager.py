import pytest
import requests
from testing.fake_response import MockResponse
from mib.rao.notification_manager import NotificationManager
class TestNotificationManager:

    def test_get_notifications(self, mock_get):
        mock_get.reset(side_effects=True)
        mock_get.return_value = MockResponse(json={
            "status":"success",
            "message":"Notifications have been sent correctly",
            "data":{
                "sender_notify":[],
                "recipient_notify":[],
                "lottery_notify":[]
                }
            
        })
        code, _ = NotificationManager.get_notifications(1)
        assert code == 200
    
    @pytest.mark.parametrize("ex",[
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError
    ])
    def test_get_notifications_unexpected_resp(self, mock_get,ex):
        mock_get.reset_mock(side_effect=True)
        mock_get.side_effect = ex()
        code, _ = NotificationManager.get_notifications(1) 
        assert code == 500
