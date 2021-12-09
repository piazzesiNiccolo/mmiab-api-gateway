import pytest
import requests
from mib.rao.lottery_manager import LotteryManager
from testing.fake_response import MockResponse


class TestLotteryManager:
    def test_get_next_lottery_ok(self, mock_get):
        json = {
            "participants": [
                {"id": 1, "choice": 5},
                {"id": 2, "choice": 26},
                {"id": 39, "choice": 50},
            ]
        }
        mock_get.return_value = MockResponse(json=json)
        code, obj = LotteryManager.get_next_lottery()
        assert code == 200
        assert obj == json

    @pytest.mark.parametrize("ex", [requests.ConnectionError, requests.ConnectTimeout])
    def test_get_next_lottery_error(self, ex, mock_get):
        mock_get.side_effect = ex()
        code, obj = LotteryManager.get_next_lottery()
        assert code == 500
        assert obj == "Unexpected response from lottery microservice!"
        mock_get.reset_mock(side_effect=True)

    @pytest.mark.parametrize(
        "code, status, message",
        [
            (200, "failure", "A participant with the given id already exists"),
            (201, "success", "Participant succesfully added"),
        ],
    )
    def test_add_participant(self, code, status, message, mock_put):
        json = {"status": status, "message": message}
        mock_put.return_value = MockResponse(code=code, json=json)
        code_ret, obj = LotteryManager.add_participant(1, 15)
        assert code_ret == code
        assert obj == json

    @pytest.mark.parametrize("ex", [requests.ConnectionError, requests.ConnectTimeout])
    def test_participate_error(self, ex, mock_put):
        mock_put.side_effect = ex()
        code, obj = LotteryManager.add_participant(1, 15)
        assert code == 500
        assert obj == "Unexpected response from lottery microservice!"
        mock_put.reset_mock(side_effect=True)

    @pytest.mark.parametrize(
        "code, json, choice",
        [
            (200, {"choice": 10}, 10),
            (
                404,
                {
                    "status": "failed",
                    "message": "No user with the given participant id found",
                },
                None,
            ),
        ],
    )
    def test_get_participant(self, code, json, choice, mock_get):
        mock_get.return_value = MockResponse(code=code, json=json)
        code_ret, choice_ret = LotteryManager.get_participant(2)
        assert code_ret == code
        assert choice_ret == choice

    @pytest.mark.parametrize("ex", [requests.ConnectionError, requests.ConnectTimeout])
    def test_get_participant_error(self, ex, mock_get):
        mock_get.side_effect = ex()
        code, obj = LotteryManager.get_participant(1)
        assert code == 500
        assert obj == "Unexpected response from lottery microservice!"
        mock_get.reset_mock(side_effect=True)
