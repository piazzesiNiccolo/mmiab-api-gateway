from flask.helpers import get_flashed_messages
import pytest
import mock
from mock import PropertyMock
import flask
from datetime import datetime
from flask import session
from mib.rao.message import Message
from mib.rao.timeline import Timeline


class TestViewMessages:
    @pytest.mark.parametrize(
        "code, message",
        [
            (200, "draft deleted"),
            (404, "draft not found for delete"),
            (403, "user not allowed to delete draft"),
        ],
    )
    def test_delete_draft(self, test_client, mock_current_user, code, message):
        with mock.patch("mib.rao.message_manager.MessageManager.delete_draft") as m:
            m.return_value = code, message
            response = test_client.get("/draft/1/delete")
            assert message in flask.get_flashed_messages()
            assert response.status_code == 302

    @pytest.mark.parametrize(
        "code, message",
        [
            (200, "message deleted"),
            (404, "message not found for delete"),
            (403, "user not allowed to delete"),
        ],
    )
    def test_delete_read_message(self, test_client, mock_current_user, code, message):
        with mock.patch(
            "mib.rao.message_manager.MessageManager.delete_read_message"
        ) as m:
            m.return_value = code, message
            response = test_client.get("/message/1/delete")
            assert message in flask.get_flashed_messages()
            assert response.status_code == 302

    @pytest.mark.parametrize(
        "code, message",
        [
            (200, "message withdrawn"),
            (404, "message not found for withdraw"),
            (403, "user not allowed to withdraw"),
        ],
    )
    def test_withdraw_message(self, test_client, mock_current_user, code, message):
        with mock.patch("mib.rao.message_manager.MessageManager.withdraw_message") as m:
            m.return_value = code, message
            response = test_client.get("/message/1/withdraw")
            assert message in flask.get_flashed_messages()
            assert response.status_code == 302

    @pytest.mark.parametrize(
        "codef, codep, msg",
        [
            (200, 201, Message(message_body="test body")),
            (404, 201, Message(message_body="test body")),
            (200, 404, Message(message_body="test body")),
        ],
    )
    def test_forward_message(self, test_client, mock_current_user, codef, codep, msg):
        with mock.patch("mib.rao.message_manager.MessageManager.forward_message") as fm:
            with mock.patch("mib.rao.message_manager.MessageManager.post_draft") as pm:
                with mock.patch("flask.url_for") as ufm:
                    fm.return_value = codef, msg, "test_message_fail"
                    pm.return_value = codep, 1
                    ufm.return_value = "/"
                    respose = test_client.get("message/1/forward")
                    assert respose.status_code == 302
                    if codef != 200:
                        assert "test_message_fail" in flask.get_flashed_messages()
                    if codep != 201:
                        assert (
                            "Something went wrong while creating a new draft"
                            in flask.get_flashed_messages()
                        )

    @pytest.mark.parametrize("code", [200, 404])
    def test_reply_to_message(self, test_client, mock_current_user, code):
        with mock.patch("mib.rao.message_manager.MessageManager.reply_to_message") as m:
            m.return_value = code, "test_message_fail"
            response = test_client.get("/message/1/reply")
            assert response.status_code == 302
            if code != 200:
                assert "test_message_fail" in flask.get_flashed_messages()

    @pytest.mark.parametrize(
        "code, message",
        [
            (200, "message sent"),
            (404, "message not found for send"),
            (403, "user not allowed to send"),
        ],
    )
    def test_send_message(self, test_client, mock_current_user, code, message):
        with mock.patch("mib.rao.message_manager.MessageManager.send_message") as m:
            m.return_value = code, message
            response = test_client.get("/message/1/send")
            assert message in flask.get_flashed_messages()
            assert response.status_code == 302

    @pytest.mark.parametrize(
        "code, obj, message",
        [
            (
                200,
                (
                    Message(id_sender=1, body_message="test body"),
                    {1: {"first_name": "fn", "last_name": "ln"}},
                    {},
                    {},
                ),
                "message read",
            ),
            (404, (None, {}, {}, {}), "message not found for read"),
            (403, (None, {}, {}, {}), "user not allowed to read"),
        ],
    )
    def test_read_message(self, test_client, mock_current_user, code, obj, message):
        with mock.patch("mib.rao.message_manager.MessageManager.get_message") as m:
            m.return_value = code, obj, message
            response = test_client.get("/message/1/read")
            if code != 200:
                assert response.status_code == 302
                assert message in flask.get_flashed_messages()
            else:
                assert response.status_code == 200

    @pytest.mark.parametrize(
        "code, obj, recipients",
        [
            (
                200,
                [
                    Message(
                        id_message=1,
                        id_sender=1,
                        is_sent=False,
                        is_arrived=False,
                        body_message="test body",
                    )
                ],
                {1: {"first_name": "fn", "last_name": "ln"}},
            ),
            (401, [], {}),
        ],
    )
    def test_list_drafts(self, test_client, mock_current_user, code, obj, recipients):
        with mock.patch("mib.rao.message_manager.MessageManager.retrieve_drafts") as m:
            m.return_value = code, obj, recipients
            response = test_client.get("/message/list/draft")
            assert response.status_code == 200
            if code != 200:
                assert (
                    "Unexpected response from messages microservice!"
                    in flask.get_flashed_messages()
                )

    @pytest.mark.parametrize(
        "code, obj, recipients",
        [
            (
                200,
                [
                    Message(
                        id_message=1,
                        id_sender=1,
                        is_sent=True,
                        body_message="test body",
                    )
                ],
                {1: {"first_name": "fn", "last_name": "ln"}},
            ),
            (401, [], {}),
        ],
    )
    def test_list_sent_messages(
        self, test_client, mock_current_user, code, obj, recipients
    ):
        with mock.patch(
            "mib.rao.message_manager.MessageManager.retrieve_sent_messages"
        ) as m:
            type(mock_current_user.return_value).lottery_points = PropertyMock(return_value = 0)
            m.return_value = code, obj, recipients
            response = test_client.get("/message/list/sent")
            assert response.status_code == 200
            if code != 200:
                assert (
                    "Unexpected response from messages microservice!"
                    in flask.get_flashed_messages()
                )

    @pytest.mark.parametrize(
        "code, obj, recipients",
        [
            (
                200,
                [
                    Message(
                        id_message=1,
                        id_sender=1,
                        is_sent=True,
                        body_message="test body",
                    )
                ],
                {1: {"first_name": "fn", "last_name": "ln"}},
            ),
            (401, [], {}),
        ],
    )
    def test_list_sent_messages_timeline(
        self, test_client, mock_current_user, code, obj, recipients
    ):
        with mock.patch(
            "mib.rao.message_manager.MessageManager.retrieve_sent_messages"
        ) as m:
            type(mock_current_user.return_value).lottery_points = PropertyMock(return_value = 0)
            m.return_value = code, obj, recipients
            response = test_client.get("/message/list/sent?y=2021&m=01&d=01")
            assert response.status_code == 200
            if code != 200:
                assert (
                    "Unexpected response from messages microservice!"
                    in flask.get_flashed_messages()
                )

    @pytest.mark.parametrize(
        "code, obj, opened, senders",
        [
            (
                200,
                [
                    Message(
                        id_message=1,
                        id_sender=1,
                        is_sent=True,
                        is_arrived=True,
                        body_message="test body",
                    )
                ],
                [False],
                {1: {"first_name": "fn", "last_name": "ln"}},
            ),
            (401, [], [], {}),
        ],
    )
    def test_list_received_messages(
        self, test_client, mock_current_user, code, obj, opened, senders
    ):
        with mock.patch(
            "mib.rao.message_manager.MessageManager.retrieve_received_messages"
        ) as m:
            m.return_value = code, obj, opened, senders
            response = test_client.get("/message/list/received")
            assert response.status_code == 200
            if code != 200:
                assert (
                    "Unexpected response from messages microservice!"
                    in flask.get_flashed_messages()
                )

    @pytest.mark.parametrize(
        "code, obj, opened, senders",
        [
            (
                200,
                [
                    Message(
                        id_message=1,
                        id_sender=1,
                        is_sent=True,
                        is_arrived=True,
                        body_message="test body",
                    )
                ],
                [False],
                {1: {"first_name": "fn", "last_name": "ln"}},
            ),
            (401, [], [], {}),
        ],
    )
    def test_list_received_messages_timeline(
        self, test_client, mock_current_user, code, obj, opened, senders
    ):
        with mock.patch(
            "mib.rao.message_manager.MessageManager.retrieve_received_messages"
        ) as m:
            m.return_value = code, obj, opened, senders
            response = test_client.get("/message/list/received?y=2021&m=01&d=01")
            assert response.status_code == 200
            if code != 200:
                assert (
                    "Unexpected response from messages microservice!"
                    in flask.get_flashed_messages()
                )

    @pytest.mark.parametrize(
        "code, rcps, data, url, validate",
        [
            (
                201,
                [(2, "fra")],
                {
                    "id_sender": 1,
                    "message_body": "hello world",
                    "delivery_date": "2022-07-07T10:05",
                    "recipients-0-recipient": "2",
                },
                "",
                True,
            ),
            (
                201,
                [(2, "fra")],
                {
                    "id_sender": 1,
                    "message_body": "hello world",
                    "delivery_date": "2022-07-07T10:05",
                    "recipients-0-recipient": "2",
                },
                "?reply_to=1",
                True,
            ),
            (
                201,
                [(2, "fra")],
                {
                    "id_sender": 1,
                    "message_bodyy": "hello world",
                    "delivery_date": "2022-07-07T10:05",
                    "recipients-0-recipient": "2",
                },
                "",
                False,
            ),
            (
                403,
                [(2, "fra")],
                {
                    "id_sender": 1,
                    "message_body": "hello world",
                    "delivery_date": "2022-07-07T10:05",
                    "recipients-0-recipient": "2",
                },
                "",
                True,
            ),
        ],
    )
    def test_post_draft(
        self, test_client, mock_current_user, code, rcps, data, url, validate
    ):
        with mock.patch("mib.rao.message_manager.MessageManager.post_draft") as m:
            with mock.patch("mib.rao.user_manager.UserManager.get_recipients") as mrcp:
                with mock.patch(
                    "mib.rao.message_manager.MessageManager.get_replying_info"
                ) as rpm:
                    rpm.return_value = {} if url != "" else None
                    mrcp.return_value = rcps
                    m.return_value = code, ""
                    response = test_client.post("/draft" + url, data=data)
                    assert response.status_code == (302 if validate else 200)
                    if code != 201:
                        assert "Something went wrong while creating a new draft"

    def test_get_draft(self, test_client, mock_current_user):
        with mock.patch("mib.rao.user_manager.UserManager.get_recipients") as mrcp:
            mrcp.return_value = [(2, "fra")]
            response = test_client.get("/draft")
            assert response.status_code == 200

    @pytest.mark.parametrize(
        "gcode, code, rcps, data, url, validate",
        [
            (
                200,
                201,
                [(2, "fra")],
                {
                    "id_sender": 1,
                    "message_body": "hello world",
                    "delivery_date": "2022-07-07T10:05",
                    "recipients-0-recipient": "2",
                },
                "",
                True,
            ),
            (
                404,
                201,
                [(2, "fra")],
                {
                    "id_sender": 1,
                    "message_body": "hello world",
                    "delivery_date": "2022-07-07T10:05",
                    "recipients-0-recipient": "2",
                },
                "",
                True,
            ),
            (
                200,
                201,
                [(2, "fra")],
                {
                    "id_sender": 1,
                    "message_bodyy": "hello world",
                    "delivery_date": "2022-07-07T10:05",
                    "recipients-0-recipient": "2",
                },
                "",
                False,
            ),
            (
                200,
                403,
                [(2, "fra")],
                {
                    "id_sender": 1,
                    "message_body": "hello world",
                    "delivery_date": "2022-07-07T10:05",
                    "recipients-0-recipient": "2",
                },
                "",
                True,
            ),
        ],
    )
    def test_post_draft_edit(
        self, test_client, mock_current_user, gcode, code, rcps, data, url, validate
    ):
        with mock.patch("mib.rao.message_manager.MessageManager.put_draft") as m:
            with mock.patch("mib.rao.user_manager.UserManager.get_recipients") as mrcp:
                with mock.patch(
                    "mib.rao.message_manager.MessageManager.get_message"
                ) as gm:
                    gm.return_value = gcode, (Message(), {}, {}, None), ""
                    mrcp.return_value = rcps
                    m.return_value = code
                    response = test_client.post("/draft/1/edit" + url, data=data)
                    assert response.status_code == (302 if validate else 200)
                    if code != 201:
                        assert "Something went wrong while creating a new draft"

    @pytest.mark.parametrize(
        "gmcode,message",
        [(500, "Unexpected response from message microservice!"), (200, "")],
    )
    def test_get_draft_edit(self, test_client, mock_current_user, gmcode, message):
        with mock.patch("mib.rao.user_manager.UserManager.get_recipients") as mrcp:
            with mock.patch("mib.rao.message_manager.MessageManager.get_message") as gm:
                gm.return_value = gmcode, (Message(), {}, {}, None), message
                mrcp.return_value = [(2, "fra")]
                response = test_client.get("/draft/1/edit")
                if gmcode == 500:
                    assert message in get_flashed_messages()
                    assert response.status_code == 302
                else:
                    assert response.status_code == 200

    @pytest.mark.parametrize(
        "url, code, obj",
        [
            (
                "?y=2021&m=11",
                200,
                Timeline(sent=[0] * 31, received=[0] * 31, year=2021, month=11),
            ),
            (
                "",
                200,
                Timeline(
                    sent=[0] * 31,
                    received=[0] * 31,
                    year=datetime.today().year,
                    month=datetime.today().month,
                ),
            ),
            ("", 404, None),
        ],
    )
    def test_list_timeline(self, test_client, mock_current_user, url, code, obj):
        with mock.patch(
            "mib.rao.message_manager.MessageManager.get_timeline_month"
        ) as m:
            m.return_value = code, obj
            response = test_client.get("/timeline" + url)
            if code != 200:
                assert (
                    "Unexpected response from messages microservice!"
                    in flask.get_flashed_messages()
                )
                assert response.status_code == 302
            else:
                assert response.status_code == 200
