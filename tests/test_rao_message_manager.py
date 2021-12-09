import io
from datetime import datetime
import mock
import base64
import requests
from werkzeug.datastructures import FileStorage
from testing.fake_response import MockResponse
from mib.rao.message_manager import MessageManager
from mib.rao.message import Message
from mib.forms.draft import EditMessageForm
import pytest

test_message_create = {
    "id_sender": 1,
    "recipients": [2, 3],
    "message_body": "hello",
    "img_path": "",
    "delivery_date": "10/01/2022 12:30",
    "is_sent": False,
    "is_arrived": False,
    "to_filter": False,
    "reply_to": None,
}
test_message_update = test_message_create.copy()
test_message_update["body"] = "hello2"


class TestMessageManager:
    @pytest.mark.parametrize(
        "code, message",
        [
            (200, "Message sent"),
            (404, "Message not found"),
            (401, "User not allowed to read the message"),
        ],
    )
    def test_send_message(self, mock_post, code, message):
        mock_post.reset_mock(side_effect=True)
        mock_post.return_value = MockResponse(
            code=code,
            json={
                "message": message,
            },
        )
        code_r, message_r = MessageManager.send_message(1, 1)
        assert code_r == code
        assert message_r == message

    @pytest.mark.parametrize(
        "exception",
        [
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ],
    )
    def test_send_message_error(self, mock_post, exception):
        mock_post.reset_mock(side_effect=True)
        mock_post.side_effect = exception()
        code_r, message_r = MessageManager.send_message(1, 1)
        assert code_r == 500
        assert message_r == "Unexpected response from messages microservice!"

    @pytest.mark.parametrize(
        "code, message",
        [
            (200, "Draft deleted"),
            (404, "Draft not found"),
            (403, "User not allowed to delete the draft"),
        ],
    )
    def test_delete_draft(self, mock_del, code, message):
        mock_del.reset_mock(side_effect=True)
        mock_del.return_value = MockResponse(
            code=code,
            json={
                "message": message,
            },
        )
        code_r, message_r = MessageManager.delete_draft(1, 1)
        assert code_r == code
        assert message_r == message

    @pytest.mark.parametrize(
        "exception",
        [
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ],
    )
    def test_delete_draft_error(self, mock_del, exception):
        mock_del.reset_mock(side_effect=True)
        mock_del.side_effect = exception()
        code_r, message_r = MessageManager.delete_draft(1, 1)
        assert code_r == 500
        assert message_r == "Unexpected response from messages microservice!"

    @pytest.mark.parametrize(
        "code, message",
        [
            (200, "Read message deleted"),
            (404, "Message not found"),
            (403, "User not allowed to delete the message"),
        ],
    )
    def test_delete_read_message(self, mock_del, code, message):
        mock_del.reset_mock(side_effect=True)
        mock_del.return_value = MockResponse(
            code=code,
            json={
                "message": message,
            },
        )
        code_r, message_r = MessageManager.delete_read_message(1, 1)
        assert code_r == code
        assert message_r == message

    @pytest.mark.parametrize(
        "exception",
        [
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ],
    )
    def test_delete_read_message_error(self, mock_del, exception):
        mock_del.reset_mock(side_effect=True)
        mock_del.side_effect = exception()
        code_r, message_r = MessageManager.delete_read_message(1, 1)
        assert code_r == 500
        assert message_r == "Unexpected response from messages microservice!"

    @pytest.mark.parametrize(
        "code, message",
        [
            (200, "Message withdraws"),
            (404, "Message not found"),
            (403, "User not allowed to withdraw the draft"),
        ],
    )
    def test_withdraw_message(self, mock_post, code, message):
        mock_post.reset_mock(side_effect=True)
        mock_post.return_value = MockResponse(
            code=code,
            json={
                "message": message,
            },
        )
        code_r, message_r = MessageManager.withdraw_message(1, 1)
        assert code_r == code
        assert message_r == message

    @pytest.mark.parametrize(
        "exception",
        [
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ],
    )
    def test_withdraw_message_error(self, mock_post, exception):
        mock_post.reset_mock(side_effect=True)
        mock_post.side_effect = exception()
        code_r, message_r = MessageManager.withdraw_message(1, 1)
        assert code_r == 500
        assert message_r == "Unexpected response from messages microservice!"

    @pytest.mark.parametrize(
        "code, message",
        [
            (200, "Message replyable"),
            (404, "Message not found"),
            (403, "User not allowed to reply to the draft"),
        ],
    )
    def test_reply_to_message(self, mock_post, code, message):
        mock_post.reset_mock(side_effect=True)
        mock_post.return_value = MockResponse(
            code=code,
            json={
                "message": message,
            },
        )
        code_r, message_r = MessageManager.reply_to_message(1, 1)
        assert code_r == code
        assert message_r == message

    @pytest.mark.parametrize(
        "exception",
        [
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ],
    )
    def test_reply_to_message_error(self, mock_post, exception):
        mock_post.reset_mock(side_effect=True)
        mock_post.side_effect = exception()
        code_r, message_r = MessageManager.reply_to_message(1, 1)
        assert code_r == 500
        assert message_r == "Unexpected response from messages microservice!"

    @pytest.mark.parametrize(
        "code, message, obj",
        [
            (200, "Message replyable", {}),
            (404, "Message not found", {}),
            (403, "User not allowed to reply to the draft", {}),
        ],
    )
    def test_forward_message(self, mock_post, code, message, obj):
        mock_post.reset_mock(side_effect=True)
        mock_post.return_value = MockResponse(
            code=code,
            json={
                "message": message,
                "obj": obj,
            },
        )
        code_r, obj_r, message_r = MessageManager.forward_message(1, 1)
        assert code_r == code
        assert message_r == message
        if code != 200:
            assert obj_r == None

    @pytest.mark.parametrize(
        "exception",
        [
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ],
    )
    def test_forward_message_error(self, mock_post, exception):
        mock_post.reset_mock(side_effect=True)
        mock_post.side_effect = exception()
        code_r, obj_r, message_r = MessageManager.forward_message(1, 1)
        assert code_r == 500
        assert message_r == "Unexpected response from messages microservice!"
        assert obj_r == None

    @pytest.mark.parametrize(
        "code, obj, message",
        [
            (200, test_message_create, "Message retrieved"),
            (404, {}, "Message not found"),
            (401, {}, "User not allowed to read the message"),
        ],
    )
    def test_get_message(self, mock_get, code, obj, message):
        mock_get.reset_mock(side_effect=True)
        mock_get.return_value = MockResponse(
            code=code,
            json={
                "message": message,
                "obj": obj,
                "users": {1: {"test": "test value"}},
                "replying_info": {},
                "image": {},
            },
        )
        code_r, obj_r, message_r = MessageManager.get_message(1, 1)
        assert code_r == code
        if code == 200:
            (msg_r, _, _, _) = obj_r
            for k in obj:
                getattr(msg_r, k) == obj[k]
        else:
            assert obj_r == None
        assert message_r == message

    @pytest.mark.parametrize(
        "exception",
        [requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout],
    )
    def test_get_message_error(self, mock_get, exception):
        mock_get.reset_mock(side_effect=True)
        mock_get.side_effect = exception()
        code, obj, message = MessageManager.get_message(1, 1)
        assert code == 500
        assert obj == None
        assert message == "Unexpected response from messages microservice!"

    @pytest.mark.parametrize(
        "code, data, endurl, messages",
        [
            (200, None, "/1", [test_message_create] * 5),
            (404, None, "/1", []),
            (400, None, "/1", []),
            (
                200,
                datetime(2022, 10, 10),
                "/1?y=2022&m=10&d=10",
                [test_message_create] * 3,
            ),
        ],
    )
    def test_retrieve_received_messages(self, mock_get, code, data, endurl, messages):
        mock_get.reset_mock(side_effect=True)

        mock_get.return_value = MockResponse(
            code=code,
            json={
                "status": "success",
                "messages": messages,
                "senders": {},
                "has_opened": {},
                "images": [],
            },
        )
        _code, obj, opened, senders = MessageManager.retrieve_received_messages(
            1, data=data
        )
        assert mock_get.called
        assert mock_get.call_args.args[0].endswith(endurl)
        assert _code == code
        assert len(obj) == len(messages)
        assert len(senders.keys()) == 0
        assert len(opened) == 0

    @pytest.mark.parametrize(
        "exception",
        [requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout],
    )
    def test_retrieve_received_messages_error(self, mock_get, exception):
        mock_get.reset_mock(side_effect=True)
        mock_get.side_effect = exception()
        code, obj, opened, senders = MessageManager.retrieve_received_messages(1)
        assert code == 500
        assert obj == []
        assert opened == []
        assert senders == {}
        mock_get.reset_mock(side_effect=True)

    @pytest.mark.parametrize(
        "code, messages",
        [
            (200, [test_message_create] * 5),
            (404, []),
            (400, []),
        ],
    )
    def test_retrieve_drafts(self, mock_get, code, messages):
        mock_get.reset_mock(side_effect=True)

        mock_get.return_value = MockResponse(
            code=code,
            json={
                "status": "success",
                "messages": messages,
                "recipients": {},
                "images": [],
            },
        )
        _code, obj, recipients = MessageManager.retrieve_drafts(1)
        assert _code == code
        assert len(obj) == len(messages)
        assert len(recipients.keys()) == 0

    @pytest.mark.parametrize(
        "exception",
        [requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout],
    )
    def test_retrieve_drafts_error(self, mock_get, exception):
        mock_get.reset_mock(side_effect=True)
        mock_get.side_effect = exception()
        code, obj, recipients = MessageManager.retrieve_drafts(1)
        assert code == 500
        assert obj == []
        assert recipients == {}
        mock_get.reset_mock(side_effect=True)

    @pytest.mark.parametrize(
        "code, data, endurl, messages",
        [
            (200, None, "/1", [test_message_create] * 5),
            (404, None, "/1", []),
            (400, None, "/1", []),
            (
                200,
                datetime(2022, 10, 10),
                "/1?y=2022&m=10&d=10",
                [test_message_create] * 3,
            ),
        ],
    )
    def test_retrieve_sent_messages(self, mock_get, code, data, endurl, messages):
        mock_get.reset_mock(side_effect=True)
        mock_get.return_value = MockResponse(
            code=code,
            json={
                "status": "success",
                "messages": messages,
                "recipients": {},
                "images": [],
            },
        )
        _code, obj, recipients = MessageManager.retrieve_sent_messages(1, data=data)
        assert mock_get.called
        assert mock_get.call_args.args[0].endswith(endurl)
        assert _code == code
        assert len(obj) == len(messages)
        assert len(recipients.keys()) == 0

    @pytest.mark.parametrize(
        "exception",
        [requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout],
    )
    def test_get_sent_messages_error(self, mock_get, exception):
        mock_get.reset_mock(side_effect=True)
        mock_get.side_effect = exception()
        code, obj, recipients = MessageManager.retrieve_sent_messages(1)
        assert code == 500
        assert obj == []
        assert recipients == {}
        mock_get.reset_mock(side_effect=True)

    def test_get_timeline_month(self, mock_get):
        _today = datetime.today()
        mock_get.reset_mock(side_effect=True)
        mock_get.return_value = MockResponse(
            code=200,
            json={
                "status": "success",
                "sent": [0] * 31,
                "received": [0] * 31,
                "year": _today.year,
                "month": _today.month,
            },
        )
        code, timeline = MessageManager.get_timeline_month(1, _today)
        assert code == 200
        assert timeline.year == _today.year
        assert timeline.month == _today.month
        assert len(timeline.sent) == 31
        assert all(map(lambda n: n == 0, timeline.sent))
        assert len(timeline.received) == 31
        assert all(map(lambda n: n == 0, timeline.received))

    @pytest.mark.parametrize(
        "exception",
        [requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout],
    )
    def test_get_timeline_month_error(self, mock_get, exception):
        mock_get.reset_mock(side_effect=True)
        mock_get.side_effect = exception()
        code, timeline = MessageManager.get_timeline_month(1, datetime.today())
        assert code == 500
        assert timeline == None
        mock_get.reset_mock(side_effect=True)

    def test_form_to_dict(self):
        form = EditMessageForm()
        dict = MessageManager.form_to_dict(form)
        assert dict == {"recipients": []}

    @pytest.mark.parametrize("date", (datetime(2021, 10, 10, hour=10, minute=10), None))
    def test_format_draft_data(self, date):
        with mock.patch.object(FileStorage, "save", autospec=True, return_value=None):
            file = FileStorage(filename="test.png", stream=io.BytesIO(b"data data"))
            dict = {
                "message_body": "test",
                "recipients": [{"recipient": "1"}, {"recipient": "2"}],
                "delivery_date": date,
                "image": file,
            }
            res = MessageManager.format_draft_data(dict, 3)
            assert res["id_sender"] == 3
            assert res["message_body"] == "test"
            assert res["recipients"] == [1, 2]
            assert (
                base64.b64decode(res["image"]["data"].encode("utf-8")) == b"data data"
            )

    @pytest.mark.parametrize(
        "code, dict",
        [
            (201, {"id_message": 3}),
            (404, {}),
        ],
    )
    def test_post_draft(self, mock_post, code, dict):
        mock_post.reset_mock(side_effect=True)
        mock_post.return_value = MockResponse(code=code, json=dict)

        _code, _id = MessageManager.post_draft({}, 1)
        assert _code == code
        assert _id == (3 if _code == 201 else None)

    @pytest.mark.parametrize(
        "exception",
        [
            requests.exceptions.ConnectTimeout,
            requests.exceptions.Timeout,
        ],
    )
    def test_post_draft_error(self, mock_post, exception):
        mock_post.reset_mock(side_effect=True)
        mock_post.side_effect = exception()

        _code, _id = MessageManager.post_draft({}, 1)
        assert _code == 500
        assert _id == None

    @pytest.mark.parametrize(
        "code",
        [
            201,
            404,
        ],
    )
    def test_put_draft(self, mock_put, code):
        mock_put.reset_mock(side_effect=True)
        mock_put.return_value = MockResponse(code=code, json={})

        _code = MessageManager.put_draft({}, 1, 1)
        assert _code == code

    @pytest.mark.parametrize(
        "exception",
        [
            requests.exceptions.ConnectTimeout,
            requests.exceptions.Timeout,
        ],
    )
    def test_put_draft_error(self, mock_put, exception):
        mock_put.reset_mock(side_effect=True)
        mock_put.side_effect = exception()

        _code = MessageManager.put_draft({}, 1, 1)
        assert _code == 500

    @pytest.mark.parametrize(
        "code, id_message, obj, users, res",
        [
            (200, None, {}, {}, None),
            (200, 1, {}, {}, None),
            (
                200,
                1,
                {"message_body": "test", "id_sender": 1, "delivery_date": None},
                {},
                {
                    "message": {
                        "message_body": "test",
                        "delivery_date": None,
                        "id_sender": 1,
                    },
                    "user": {"first_name": "Anonymous", "id": 0, "last_name": ""},
                },
            ),
            (
                200,
                1,
                {"message_body": "test", "id_sender": 1, "delivery_date": None},
                {2: {"first_name": "fn", "last_name": "ln"}},
                {
                    "message": {
                        "message_body": "test",
                        "delivery_date": None,
                        "id_sender": 1,
                    },
                    "user": {"first_name": "Anonymous", "id": 0, "last_name": ""},
                },
            ),
            (
                200,
                1,
                {"message_body": "test", "id_sender": 1, "delivery_date": None},
                {1: {"first_name": "fn", "last_name": "ln"}},
                {
                    "message": {
                        "message_body": "test",
                        "delivery_date": None,
                        "id_sender": 1,
                    },
                    "user": {"first_name": "fn", "id": 1, "last_name": "ln"},
                },
            ),
            (
                404,
                1,
                {"message_body": "test", "id_sender": 1, "delivery_date": None},
                {1: {"first_name": "fn", "last_name": "ln"}},
                None,
            ),
        ],
    )
    def test_get_replying_info(self, mock_get, code, id_message, obj, users, res):
        with mock.patch("mib.rao.message_manager.MessageManager.get_message") as m:
            mock_get.return_value = MockResponse(
                code=code,
                json={
                    "obj": obj,
                    "users": users,
                },
            )
            _res = MessageManager.get_replying_info(id_message, 1)
            assert _res == res

    @pytest.mark.parametrize(
        "exception",
        [
            requests.exceptions.ConnectTimeout,
            requests.exceptions.Timeout,
        ],
    )
    def test_get_replying_info_error(self, mock_get, exception):
        mock_get.reset_mock(side_effect=True)
        mock_get.side_effect = exception()
        _res = MessageManager.get_replying_info(1, 1)
        assert _res == None
