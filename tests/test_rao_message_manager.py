import requests
from testing.fake_response import MockResponse
from mib.rao.message_manager import MessageManager
import pytest

test_message_create = {
        'id_sender':1,
        'recipients':[2,3],
        'message_body':"hello",
        'img_path':"",
        'delivery_date':"10/01/2022 12:30",
        'is_sent':False,
        'is_arrived':False,
        'to_filter':False,
        'reply_to':None,
}
test_message_update = test_message_create.copy()
test_message_update["body"] = "hello2"

class TestMessageManager:

    @pytest.mark.parametrize("code, message, status", [ 
        (200, test_message_create, "success"),
        (404,"Message not found","failed"),
        (401,"User not allowed to read the message","failed")
    ])
    def test_read_message_expected_response(self, mock_get,code, message, status):
        mock_get.return_value= MockResponse(code=code, json={
            "status":status,
            "message":message
        })
        code_r, obj_r = MessageManager.read_message(1,1)
        assert code_r == code_r
        assert obj_r == message

    @pytest.mark.parametrize("exception",[
        requests.exceptions.ConnectionError,
        requests.exceptions.ConnectTimeout
    ])
    def test_read_message_unexpected_response(self, mock_get,exception):
        mock_get.reset_mock(side_effect=True)
        mock_get.side_effect = exception()
        code, obj = MessageManager.read_message(1,1)
        assert code == 500
        assert obj == "Unexpected response from messages microservice!"
    
    
    def test_get_sent_messages_ok_response(self, mock_get):
        mock_get.reset_mock(side_effect=True)

        mock_get.return_value = MockResponse(code=200,json={
            "status":"success",
            "messages":[test_message_create for i in range(5)],
            "recipients":[],
            "images":[]
        })
        code, obj = MessageManager.get_sended_message_by_id_user(1)
        assert code == 200
        assert len(obj) == 5
    
    @pytest.mark.parametrize("exception",[
        requests.exceptions.ConnectionError,
        requests.exceptions.ConnectTimeout
    ])
    def test_get_sent_messages_unexpected_response(self, mock_get,exception):
        mock_get.reset_mock(side_effect=True)
        mock_get.side_effect = exception()
        code, obj = MessageManager.get_sended_message_by_id_user(1)
        assert code == 500
        assert obj == "Unexpected response from messages microservice!"
        mock_get.reset_mock(side_effect=True)
