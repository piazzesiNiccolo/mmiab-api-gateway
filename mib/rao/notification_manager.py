import requests
from flask import current_app as app

class NotificationManager:
    @classmethod
    def notifications_endpoint(cls):
        return app.config['NOTIFICATIONS_MS_URL']
    
    @classmethod
    def requests_timeout_seconds(cls):
        return app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def get_notifications(cls) -> int:
        endpoint = f"{cls.notifications_endpoint()}/notifications"
        try:
            response = requests.get(endpoint, timeout=cls.requests_timeout_seconds())
            return response.status_code
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500

