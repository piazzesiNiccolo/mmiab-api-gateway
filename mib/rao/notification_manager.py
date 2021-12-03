import requests
from mib import app
from typing import Tuple

class NotificationManager:
    
    @classmethod
    def users_endpoint(cls):
        return app.config['USERS_MS_URL']
    
    @classmethod
    def requests_timeout_seconds(cls):
        return app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def get_notifications(cls) -> Tuple[int, str]:
        endpoint = f"{cls.NOTIFICATIONS_ENDPOINT}/notifications"
        try:
            response = requests.get(endpoint, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            data = response.json()
            notifications = data.get("data")
            return response.status_code, notifications
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected reponse from user microservice"

    @classmethod
    def add_notifications(cls, data) -> int:
        endpoint = f'{cls.NOTIFICATIONS_ENDPOINT}/notifications/add'
        try:
            response = requests.post(endpoint, data=data, timeout=cls.REQUESTS_TIMEOUT_SECONDS)
            return response.status_code
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return 500, "Unexpected reponse from user microservice"
        

