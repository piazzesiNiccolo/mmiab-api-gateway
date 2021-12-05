import datetime
from datetime import timedelta
import calendar
from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_login import (login_user, login_required)
from flask_login import current_user

from typing import Text

from mib.forms.draft import EditMessageForm
from mib.rao.message_manager import MessageManager
from mib.rao.user_manager import UserManager
from mib.auth.user import User


messages = Blueprint('messages', __name__)

@messages.route('/draft/<int:id>/delete', methods=['GET'])
@login_required
def delete_draft(id):
    _, message = MessageManager.delete_draft(id, current_user.id)
    flash(message)
    return redirect(url_for('messages.list_drafts'))

@messages.route('/message/<int:id>/delete', methods=['GET'])
@login_required
def delete_read_message(id):
    _, message = MessageManager.delete_read_message(id, current_user.id)
    flash(message)
    return redirect(url_for('messages.list_received_messages'))

@messages.route('/message/<int:id>/withdraw', methods=['GET'])
@login_required
def withdraw_message(id):
    _, message = MessageManager.withdraw_message(id, current_user.id)
    flash(message)
    return redirect(url_for('messages.list_sent_messages'))

@messages.route('/message/<int:id>/forward', methods=['GET'])
@login_required
def forward_message(id):
    pass

@messages.route('/message/<int:id>/reply', methods=['GET'])
@login_required
def reply_to_message(id):
    pass


@messages.route("/message/<int:id>/read", methods=["GET"])
@login_required
def read_messages(id):
    """
    Let the user read the selected message
    """
    code, obj, message = MessageManager.get_message(id,current_user.id)
    if code != 200:
        flash(message)
        return redirect(url_for('messages.list_received_messages'))

    (msg, users, image) = obj
    
    return render_template(
        'read_message.html',
        message=msg,
        users=users,
        image=image
    )

'''
@messages.route("/message/list/sent", methods=["GET"])
@login_required
def mailbox_list_sent():
    """
    Displays messages sent by current user
    :return: sent messages mailbox template
    """
    if current_user.is_authenticated:
        code, obj = MessageManager.get_sended_message_by_id_user(current_user.id)
    
    if code != 200:
        flash("Error while retriving the message")
        #TODO check return in case of failure
        #return redirect(url_for('mai'))
        #return mailbox


    return render_template(
        "mailbox.html",
        message_list=obj,
        list_type="sent",
        withdraw=current_user.lottery_points > 0,
    )
'''


@messages.route("/message/list/draft", methods=["GET"])
@login_required
def list_drafts():
    """
    Displays messages sent by current user
    :return: sent messages mailbox template
    """
    code, messages = MessageManager.retrieve_drafts(current_user.id)
    
    if code != 200:
        flash("Unexpected response from messages microservice!")
        #TODO check return in case of failure
        #return redirect(url_for('mai'))
        #return mailbox

    return render_template(
        "mailbox.html",
        message_list=messages,
        list_type="draft",
    )

@messages.route("/message/list/sent", methods=["GET"])
@login_required
def list_sent_messages():
    ''''
    If the user specifies year, month and day, it returns the timeline
    else if the previous parameters are not specified, it returns the list of sent messages
        with no filters
    '''

    year = request.args.get('y',None)
    month = request.args.get('m',None)
    day = request.args.get('d',None)

    try:
        today_dt = datetime(year, month, day)
    except ValueError:
        today_dt = None
        
    code, messages = MessageManager.retrieve_sent_messages(current_user.id, dt=today_dt)
    if code != 200:
        flash("Unexpected response from messages microservice!")

    tomorrow = today_dt + timedelta(days=1) if today_dt is not None else None
    yesterday = today_dt - timedelta(days=1) if today_dt is not None else None
    day_view = today_dt is not None

    return render_template(
        "mailbox.html",
        message_list=messages,
        tomorrow=tomorrow,
        yesterday=yesterday,
        day_view=day_view,
        list_type="sent",
    )

@messages.route("/message/list/received", methods=["GET"])
@login_required
def list_received_messages():
    ''''
    If the user specifies year, month and day, it returns the timeline
    else if the previous parameters are not specified, it returns the list of received messages
        with no filters
    '''

    year = request.args.get('y',None)
    month = request.args.get('m',None)
    day = request.args.get('d',None)

    try:
        today_dt = datetime(year, month, day)
    except ValueError:
        today_dt = None
        
    code, obj = MessageManager.retrieve_received_messages(current_user.id, dt=today_dt)
    if code != 200:
        flash("Unexpected response from messages microservice!")

    tomorrow = today_dt + timedelta(days=1) if today_dt is not None else None
    yesterday = today_dt - timedelta(days=1) if today_dt is not None else None
    day_view = today_dt is not None

    return render_template(
        "mailbox.html",
        message_list=obj,
        tomorrow=tomorrow,
        yesterday=yesterday,
        day_view=day_view,
        list_type="received",
    )

@messages.route('/message/<int:id_message>/send', methods=['GET'])
@login_required
def send_message(id_message):
    _, message = MessageManager.send_message(id_message, current_user.get_id())
    flash(message)
    return redirect(url_for('messages.list_sent_messages'))

@messages.route('/draft/<int:id_message>', methods=["DELETE", "PUT"])
@login_required
def draft_edit(id_message):

    if request.method == 'DELETE':

        code, message = MessageManager.delete_draft(id_message, current_user.get_id())
        
        flash(message)
        return redirect(url_for('home.index'))

    elif request.method == 'PUT':
        pass

@messages.route("/timeline", methods=["GET"])
@login_required
def get_timeline_month():

    _year = request.args.get('y',None)
    _month = request.args.get('m',None)
    try:
        y_i, m_i = int(_year), int(_month)
        dt = datetime(y_i, m_i, 1)
    except (ValueError, TypeError):
        dt = datetime.today()

    first_day, number_of_days = calendar.monthrange(dt.year, dt.month)

    code , timeline = MessageManager.get_timeline_month(current_user.id, dt)
    if code != 200:
        flash("Unexpected response from messages microservice!")
        return redirect(url_for('messages.list_received_messages'))

    return render_template(
        "calendar_bs.html",
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

@messages.route('/draft', methods=["POST", "GET"])
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
            code = MessageManager.post_draft(form)

            if(code == 200):
                flash("Draft correctly created")
            return redirect(url_for('home.index'))

    return render_template(
        "draft.html",
        form=form,
        replying_info=replying_info,
        send_to=send_to,
        available_recipients=available_recipients,
    )
