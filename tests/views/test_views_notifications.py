from flask import json
import pytest

import mock

class TestViewsNotifications:
    @pytest.mark.parametrize("code, status",[ 
        (200, "success"),
        (500, "failed")
    ])
    def test_get_notifications(self, test_client, code, status):
        with mock.patch("mib.rao.notification_manager.NotificationManager.get_notifications") as m:
            m.return_value = code, {}
            resp = test_client.get("/notifications")
            assert json.loads(resp.data)["status"] == status 
            assert resp.status_code == 200
