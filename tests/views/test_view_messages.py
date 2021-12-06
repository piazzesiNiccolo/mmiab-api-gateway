import pytest
import mock
import flask
from flask import session
from mib.rao.message import Message

class TestViewMessages:

    @pytest.mark.parametrize('code, message', [
        (200, 'draft deleted'),
        (404, 'draft not found for delete'),
        (403, 'user not allowed to delete draft'),
    ])
    def test_delete_draft(self, test_client, mock_current_user, code, message):
        with mock.patch('mib.rao.message_manager.MessageManager.delete_draft') as m:
            m.return_value = code, message
            response = test_client.get('/draft/1/delete')
            assert message in flask.get_flashed_messages()
            assert response.status_code == 302

    @pytest.mark.parametrize('code, message', [
        (200, 'message deleted'),
        (404, 'message not found for delete'),
        (403, 'user not allowed to delete'),
    ])
    def test_delete_read_message(self, test_client, mock_current_user, code, message):
        with mock.patch('mib.rao.message_manager.MessageManager.delete_read_message') as m:
            m.return_value = code, message
            response = test_client.get('/message/1/delete')
            assert message in flask.get_flashed_messages()
            assert response.status_code == 302

    @pytest.mark.parametrize('code, message', [
        (200, 'message withdrawn'),
        (404, 'message not found for withdraw'),
        (403, 'user not allowed to withdraw'),
    ])
    def test_withdraw_message(self, test_client, mock_current_user, code, message):
        with mock.patch('mib.rao.message_manager.MessageManager.withdraw_message') as m:
            m.return_value = code, message
            response = test_client.get('/message/1/withdraw')
            assert message in flask.get_flashed_messages()
            assert response.status_code == 302

    @pytest.mark.parametrize('code, message', [
        (200, 'message sent'),
        (404, 'message not found for send'),
        (403, 'user not allowed to send'),
    ])
    def test_send_message(self, test_client, mock_current_user, code, message):
        with mock.patch('mib.rao.message_manager.MessageManager.send_message') as m:
            m.return_value = code, message
            response = test_client.get('/message/1/send')
            assert message in flask.get_flashed_messages()
            assert response.status_code == 302

    @pytest.mark.parametrize('code, obj, message', [
        (200, (Message(id_sender=1, body_message='test body'), {1: {'first_name': 'fn', 'last_name': 'ln'}}, {}), 'message read'),
        (404, (None, {}, {}), 'message not found for read'),
        (403, (None, {}, {}), 'user not allowed to read'),
    ])
    def test_read_message(self, test_client, mock_current_user, code, obj, message):
        with mock.patch('mib.rao.message_manager.MessageManager.get_message') as m:
            m.return_value = code, obj, message
            response = test_client.get('/message/1/read')
            if code != 200:
                assert response.status_code == 302
                assert message in flask.get_flashed_messages()
            else:
                assert response.status_code == 200

    def test_post_draft(self, test_client):

        data = {
                    "id_sender" : 1,
                    "body_message": "hello world",
                    "date_of_send": "10:05 07/07/2022",
                    "recipients-0-recipient": "2",
                }
        response = test_client.post("/draft", data=data, follow_redirects=True)
        assert response.status_code == 200
    ''''
    @pytest.mark.parametrize('code, obj', [
        (200, (Message(id_sender=1,is_sent=False,is_arrived=False, body_message='test body'),\
            {1: {'first_name': 'fn', 'last_name': 'ln'}}, {})),
        (401, (None, {}, {})),
    ])
    def test_list_drafts(self, test_client, mock_current_user, code, obj):
        with mock.patch('mib.rao.message_manager.MessageManager.retrieve_drafts') as m:
            m.return_value = code, obj, {}
            response = test_client.get('/message/list/draft')
            if code != 200:
                assert response.status_code == 401
            else:
                assert response.status_code == 200

    @pytest.mark.parametrize('code, obj', [
        (200, (Message(id_sender=1,is_sent=True, body_message='test body'),\
            {1: {'first_name': 'fn', 'last_name': 'ln'}}, {})),
        (401, (None, {}, {})),
    ])
    def test_list_sent_messages(self, test_client, mock_current_user, code, obj):
        with mock.patch('mib.rao.message_manager.MessageManager.retrieve_sent_messages') as m:
            m.return_value = code, obj, {}
            response = test_client.get('/message/list/sent')
            if code != 200:
                assert response.status_code == 401
            else:
                assert response.status_code == 200

    @pytest.mark.parametrize('code, obj', [
        (200, (Message(id_sender=1,is_sent=True, body_message='test body'),\
            {1: {'first_name': 'fn', 'last_name': 'ln'}}, {})),
        (401, (None, {}, {})),
    ])
    def test_list_sent_messages_timeline(self, test_client, mock_current_user, code, obj):
        with mock.patch('mib.rao.message_manager.MessageManager.retrieve_sent_messages') as m:
            m.return_value = code, obj, {}
            response = test_client.get('/message/list/sent?y=2021&m=01&d=01')
            if code != 200:
                assert response.status_code == 401
            else:
                assert response.status_code == 200

    @pytest.mark.parametrize('code, obj', [
        (200, (Message(id_sender=1,is_sent=True, is_arrived=True, body_message='test body'),\
            {1: {'first_name': 'fn', 'last_name': 'ln'}}, {})),
        (401, (None, {}, {})),
    ])
    def test_list_sent_messages(self, test_client, mock_current_user, code, obj):
        with mock.patch('mib.rao.message_manager.MessageManager.retrieve_received_messages') as m:
            m.return_value = code, obj, {}
            response = test_client.get('/message/list/received')
            if code != 200:
                assert response.status_code == 401
            else:
                assert response.status_code == 200

    @pytest.mark.parametrize('code, obj', [
        (200, (Message(id_sender=1,is_sent=True,is_arrived=True, body_message='test body'),\
            {1: {'first_name': 'fn', 'last_name': 'ln'}}, {})),
        (401, (None, {}, {})),
    ])
    def test_list_sent_messages_timeline(self, test_client, mock_current_user, code, obj):
        with mock.patch('mib.rao.message_manager.MessageManager.retrieve_received_messages') as m:
            m.return_value = code, obj, {}
            response = test_client.get('/message/list/received?y=2021&m=01&d=01')
            if code != 200:
                assert response.status_code == 401
            else:
                assert response.status_code == 200
    '''

    @pytest.mark.parametrize('code, obj', [
        (200, (Message(id_sender=1,is_sent=True,is_arrived=True, body_message='test body'),\
            {1: {'first_name': 'fn', 'last_name': 'ln'}}, {})),
        (401, (None, {}, {})),
    ])
    def test_list_sent_messages_timeline(self, test_client, mock_current_user, code, obj):
        with mock.patch('mib.rao.message_manager.MessageManager.get_timeline_month') as m:
            m.return_value = code, obj, {}
            response = test_client.get('/timeline?y=2021&m=01')
            if code != 200:
                assert response.status_code == 401
            else:
                assert response.status_code == 200
