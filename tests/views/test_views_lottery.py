from flask.helpers import get_flashed_messages
import pytest
import mock

class TestViewsLottery:

    def test_get_participate_form(self, test_client, mock_current_user):
        with mock.patch("mib.rao.lottery_manager.LotteryManager.get_participant") as m:
            m.return_value = 404,None
            resp = test_client.get("/lottery/participate")
            assert resp.status_code == 200
            assert b"Choose a number between 1 and 50" in resp.data

    @pytest.mark.parametrize("code, choice",[ 
        (200,14),
        (404,None),
        (500,"Unexpected response from lottery microservice!")
    ])
    def test_post_participate(self, code, choice, test_client,mock_current_user):
        with mock.patch("mib.rao.lottery_manager.LotteryManager.get_participant") as m:
            m.return_value = code, choice
            with mock.patch("mib.rao.lottery_manager.LotteryManager.add_participant") as m2:
                m2.return_value = 201, "ok"
                json = {"choice":50}
                resp = test_client.post("/lottery/participate", data=json)
                if code == 200 or code == 404:
                    assert B"You have already played with number" in resp.data
                else:
                    assert choice in get_flashed_messages()
    
    @pytest.mark.parametrize("choice",[-10, 0, 51, 120])
    def test_post_participate_invalid_choice(self, choice, test_client):
        with mock.patch("mib.rao.lottery_manager.LotteryManager.get_participant") as m:
            m.return_value = 404,None 
            resp = test_client.post("/lottery/participate",data={"choice":choice})
            assert resp.status_code == 200
            assert b"Choose a number between 1 and 50" in resp.data

    @pytest.mark.parametrize("code",[200, 500])
    def test_post_participate_cant_add(self, test_client, mock_current_user, code):
        with mock.patch("mib.rao.lottery_manager.LotteryManager.get_participant") as m:
            m.return_value = 404, None
            with mock.patch("mib.rao.lottery_manager.LotteryManager.add_participant") as m2:
                m2.return_value = code, "Unexpected response from lottery microsrrvice!"
                resp = test_client.post("/lottery/participate",data={"choice":10})
            assert resp.status_code == 200
            if code == 500:
                assert "Unexpected response from lottery microsrrvice!" in get_flashed_messages()
                assert b"Choose a number between 1 and 50" in resp.data



    @pytest.mark.parametrize("code, choice",[ 
        (200,14),
        (404,None),
        (500,"Unexpected response from lottery microservice!")
    ])
    def test_get_lottery_page(self, code, choice, test_client, mock_current_user):

        with mock.patch("mib.rao.lottery_manager.LotteryManager.get_participant") as m:
            m.return_value = code, choice
            resp = test_client.get("/lottery")
            if code == 200:
                assert resp.status_code == 200
                b"You have already played with number 14" in resp.data
            elif code == 404:
                assert resp.status_code == 200
                assert b"Choose a number between 1 and 50" in resp.data

            else:
                assert choice in get_flashed_messages()
                assert resp.status_code == 302

