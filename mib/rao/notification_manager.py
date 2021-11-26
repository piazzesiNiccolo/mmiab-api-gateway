import requests
from mib import app

class NotificationManager:
    NOTIFICATIONS_ENDPOINT = app.config['NOTIFICATIONS_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def get_notifications(cls) -> int:
        endpoint = f"{cls.NOTIFICATIONS_ENDPOINT}/notifications"
        try:
            response = requests.get(endpoint, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            return response.status_code
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500

