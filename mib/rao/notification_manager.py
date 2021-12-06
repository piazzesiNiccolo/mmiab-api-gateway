import requests
from flask import current_app as app
from typing import Tuple

class NotificationManager:
    @classmethod
    def notifications_endpoint(cls):
        return app.config['NOTIFICATIONS_MS_URL']
    
    @classmethod
    def requests_timeout_seconds(cls):
        return app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def get_notifications(cls, user_id: int) -> Tuple[int, str]:
        endpoint = f"{cls.notifications_endpoint()}/notifications/{user_id}"
        try:
            response = requests.get(endpoint, timeout=cls.requests_timeout_seconds())
            data = response.json()
            notifications = data.get("data")
            return response.status_code, notifications
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected reponse from user microservice"

        

