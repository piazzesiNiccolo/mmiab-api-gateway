import requests
from flask import current_app as app
from requests.api import request


class LotteryManager:
    """
    Wrapper class for lottery request
    """
    
    @classmethod
    def lottery_endpoint(cls):
        return app.config["LOTTERY_MS_URL"]

    @classmethod
    def requests_timeout_seconds(cls):
        return app.config["REQUESTS_TIMEOUT_SECONDS"]

    @classmethod
    def get_next_lottery(cls):
        endpoint = f"{cls.lottery_endpoint()}/lottery"
        try:
            resp = requests.get(endpoint, timeout=cls.requests_timeout_seconds())
        except (requests.ConnectionError, requests.ConnectTimeout):
            return 500, "Unexpected response from lottery microservice!"
        else:
            code = resp.status_code
            obj = resp.json()
            return code, obj

    @classmethod
    def add_participant(cls, id: int, choice: int):
        endpoint = f"{cls.lottery_endpoint()}/lottery/participate"
        json = {"id": id, "choice": choice}
        try:
            resp = requests.put(
                endpoint, json=json, timeout=cls.requests_timeout_seconds()
            )
        except (requests.ConnectionError, requests.ConnectTimeout):
            return 500, "Unexpected response from lottery microservice!"
        else:
            return resp.status_code, resp.json()

    @classmethod
    def get_participant(cls, id: int):
        endpoint = f"{cls.lottery_endpoint()}/lottery/{id}"
        try:
            resp = requests.get(endpoint, timeout=cls.requests_timeout_seconds())
        except (requests.ConnectionError, requests.ConnectTimeout):
            return 500, "Unexpected response from lottery microservice!"
        else:
            json = resp.json()
            choice = json.get("choice", None)
            return resp.status_code, choice
