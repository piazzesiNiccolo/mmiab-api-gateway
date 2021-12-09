from datetime import datetime
from datetime import timedelta
import calendar
from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_login import login_user, login_required
from flask_login import current_user

from typing import Text

from mib.forms.draft import EditMessageForm
from mib.rao.message_manager import MessageManager
from mib.rao.user_manager import UserManager
from mib.auth.user import User


messages = Blueprint("messages", __name__)


@messages.route("/draft/<int:id>/delete", methods=["GET"])
@login_required
def delete_draft(id):
    _, message = MessageManager.delete_draft(id, current_user.id)
    flash(message)
    return redirect(url_for("messages.list_drafts"))


@messages.route("/message/<int:id>/delete", methods=["GET"])
@login_required
def delete_read_message(id):
    _, message = MessageManager.delete_read_message(id, current_user.id)
    flash(message)
    return redirect(url_for("messages.list_received_messages"))


@messages.route("/message/<int:id>/withdraw", methods=["GET"])
@login_required
def withdraw_message(id):
    _, message = MessageManager.withdraw_message(id, current_user.id)
    flash(message)
    return redirect(url_for("messages.list_sent_messages"))


@messages.route("/message/<int:id>/forward", methods=["GET"])
@login_required
def forward_message(id):
    code, msg, message = MessageManager.forward_message(id, current_user.id)
    if code != 200:
        flash(message)
        return redirect(url_for("messages.list_received_messages"))

    fw_data = {
        "message_body": msg.message_body,
    }

    code, id_message = MessageManager.post_draft(fw_data, current_user.id)
    if code != 201:
        flash("Something went wrong while creating a new draft")
        return redirect(url_for("messages.list_received_messages"))

    return redirect(url_for("messages.draft_edit", id_message=id_message))


@messages.route("/message/<int:id>/reply", methods=["GET"])
@login_required
def reply_to_message(id):
    code, message = MessageManager.reply_to_message(id, current_user.id)

    if code != 200:
        flash(message)
        return redirect(url_for("messages.list_received_messages"))

    return redirect(url_for("messages.draft", reply_to=id))


@messages.route("/message/<int:id>/read", methods=["GET"])
@login_required
def read_messages(id):
    """
    Let the user read the selected message
    """
    code, obj, message = MessageManager.get_message(id, current_user.id)
    if code != 200:
        flash(message)
        return redirect(url_for("messages.list_received_messages"))

    (msg, users, image, replying_info) = obj

    return render_template(
        "read_message.html",
        message=msg,
        users=users,
        image=image,
        replying_info=replying_info,
    )


@messages.route("/message/list/draft", methods=["GET"])
@login_required
def list_drafts():
    """
    Displays messages sent by current user
    :return: sent messages mailbox template
    """
    code, messages, recipients = MessageManager.retrieve_drafts(current_user.id)

    if code != 200:
        flash("Unexpected response from messages microservice!")
        # TODO check return in case of failure
        # return redirect(url_for('mai'))
        # return mailbox

    return render_template(
        "mailbox.html",
        message_list=messages,
        recipients=recipients,
        list_type="draft",
        calendar_view=None,
    )


@messages.route("/message/list/sent", methods=["GET"])
@login_required
def list_sent_messages():
    """ '
    If the user specifies year, month and day, it returns the timeline
    else if the previous parameters are not specified, it returns the list of sent messages
        with no filters
    """

    year = request.args.get("y", None)
    month = request.args.get("m", None)
    day = request.args.get("d", None)

    try:
        y_i, m_i, d_i = int(year), int(month), int(day)
        day_dt = datetime(y_i, m_i, d_i)
    except (ValueError, TypeError):
        day_dt = None

    code, messages, recipients = MessageManager.retrieve_sent_messages(
        current_user.id, data=day_dt
    )
    if code != 200:
        flash("Unexpected response from messages microservice!")

    calendar_view = None
    if day_dt is not None:
        tomorrow = day_dt + timedelta(days=1)
        yesterday = day_dt - timedelta(days=1)
        calendar_view = {
            "today": (day_dt.year, day_dt.month, day_dt.day),
            "tomorrow": (tomorrow.year, tomorrow.month, tomorrow.day),
            "yesterday": (yesterday.year, yesterday.month, yesterday.day),
        }

    return render_template(
        "mailbox.html",
        message_list=messages,
        recipients=recipients,
        calendar_view=calendar_view,
        withdraw=(current_user.lottery_points > 0),
        list_type="sent",
    )


@messages.route("/message/list/received", methods=["GET"])
@login_required
def list_received_messages():
    """ '
    If the user specifies year, month and day, it returns the timeline
    else if the previous parameters are not specified, it returns the list of received messages
        with no filters
    """

    year = request.args.get("y", None)
    month = request.args.get("m", None)
    day = request.args.get("d", None)

    try:
        y_i, m_i, d_i = int(year), int(month), int(day)
        day_dt = datetime(y_i, m_i, d_i)
    except (ValueError, TypeError):
        day_dt = None

    code, obj, opened, senders = MessageManager.retrieve_received_messages(
        current_user.id, data=day_dt
    )
    if code != 200:
        flash("Unexpected response from messages microservice!")

    calendar_view = None
    if day_dt is not None:
        tomorrow = day_dt + timedelta(days=1)
        yesterday = day_dt - timedelta(days=1)
        calendar_view = {
            "today": (day_dt.year, day_dt.month, day_dt.day),
            "tomorrow": (tomorrow.year, tomorrow.month, tomorrow.day),
            "yesterday": (yesterday.year, yesterday.month, yesterday.day),
        }

    return render_template(
        "mailbox.html",
        message_list=obj,
        senders=senders,
        opened_dict=opened,
        calendar_view=calendar_view,
        list_type="received",
    )


@messages.route("/message/<int:id>/send", methods=["GET"])
@login_required
def send_message(id):
    _, message = MessageManager.send_message(id, current_user.get_id())
    flash(message)
    return redirect(url_for("messages.list_sent_messages"))


@messages.route("/draft/<int:id_message>/edit", methods=["GET", "POST"])
@login_required
def draft_edit(id_message):

    code, obj, message = MessageManager.get_message(id_message, current_user.id)

    if code != 200:
        flash(message)
        return redirect(url_for("messages.list_drafts"))

    draft, _, old_image, replying_info = obj

    old_recipients = draft.recipients
    form_recipients = [
        {"name": "Recipient"}
        for _ in (range(len(old_recipients)) if len(old_recipients) > 0 else range(1))
    ]
    form = EditMessageForm(recipients=form_recipients)
    available_recipients = UserManager.get_recipients(current_user.get_id())
    for recipient_form in form.recipients:
        recipient_form.recipient.choices = available_recipients

    if request.method == "POST":
        if form.validate_on_submit():

            form_data = MessageManager.form_to_dict(form)
            code = MessageManager.put_draft(form_data, current_user.id, id_message)
            if code == 201:
                # flash("Draft correctly modified")
                return redirect(url_for("messages.list_drafts"))
            else:
                flash("Something went wrong")
                return redirect(url_for("home.index"))

    return render_template(
        "draft.html",
        edit=True,
        form=form,
        old_date=draft.delivery_date,
        old_message=draft.message_body,
        old_recs=old_recipients,
        id_sender=draft.id_sender,
        replying_info=replying_info,
        available_recipients=available_recipients,
        image=old_image,
    )


@messages.route("/timeline", methods=["GET"])
@login_required
def get_timeline_month():

    _year = request.args.get("y", None)
    _month = request.args.get("m", None)
    try:
        y_i, m_i = int(_year), int(_month)
        dt = datetime(y_i, m_i, 1)
    except (ValueError, TypeError):
        dt = datetime.today()

    first_day, number_of_days = calendar.monthrange(dt.year, dt.month)

    code, timeline = MessageManager.get_timeline_month(current_user.id, dt)
    if code != 200:
        flash("Unexpected response from messages microservice!")
        return redirect(url_for("messages.list_received_messages"))

    return render_template(
        "calendar.html",
        calendar_view={
            "year": timeline.year,
            "month": timeline.month,
            "month_name": calendar.month_name[timeline.month],
            "days_in_month": number_of_days,
            "starts_with": first_day,
            "sent": timeline.sent,
            "received": timeline.received,
        },
    )


@messages.route("/draft", methods=["POST", "GET"])
@login_required
def draft():
    reply_to = request.args.get("reply_to", None)
    send_to = request.args.get("send_to", None) if reply_to is None else None
    replying_info = MessageManager.get_replying_info(reply_to, current_user.get_id())

    form = EditMessageForm(recipients=[{"name": "Recipient"}])
    available_recipients = UserManager.get_recipients(current_user.get_id())
    for recipient_form in form.recipients:
        recipient_form.recipient.choices = available_recipients
    if request.method == "POST":
        if form.validate_on_submit():
            form_data = MessageManager.form_to_dict(form)
            if replying_info is not None:
                form_data["reply_to"] = int(reply_to)
            code, _ = MessageManager.post_draft(form_data, current_user.id)
            if code == 201:
                # flash("Draft correctly created")
                return redirect(url_for("messages.list_drafts"))
            else:
                flash("Something went wrong while creating a new draft")
                return redirect(url_for("home.index"))

    return render_template(
        "draft.html",
        form=form,
        replying_info=replying_info,
        send_to=send_to,
        available_recipients=available_recipients,
    )
