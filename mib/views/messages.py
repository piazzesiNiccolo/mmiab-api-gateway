import datetime
from datetime import timedelta
import calendar
from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_login import (login_user, login_required)
from flask_login import current_user

from typing import Text

from mib.rao.message_manager import MessageManager
from mib.auth.user import User

messages = Blueprint('messages', __name__)


@messages.route("/message/{id}/read", methods=["GET"])
@login_required
def read_messages(id):

    """
    Let the user read the selected message
    """

    code, obj = MessageManager.read_message(id,current_user.id)
    if code != 200:
        flash("Error while retriving the message")
        #TODO check return in case of failure
        #return redirect(url_for('mai'))
        #return mailbox 
    
    return render_template('read_message.html', message=obj)

@messages.route("/message/list/sent", methods=["GET"])
@login_required
def mailbox_list_sent():
    """
    Displays messages sent by current user
    :return: sent messages mailbox template
    """
    message_list = []
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


@messages.route("/message/list/draft", methods=["GET"])
@login_required
def mailbox_list_drafted():
    """
    Displays messages sent by current user
    :return: sent messages mailbox template
    """
    message_list = []
    if current_user.is_authenticated:
        code, obj = MessageManager.get_drafted_message_by_id_user(current_user.id)
    
    if code != 200:
        flash("Error while retriving the message")
        #TODO check return in case of failure
        #return redirect(url_for('mai'))
        #return mailbox


    return render_template(
        "mailbox.html",
        message_list=obj,
        list_type="drafted",
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
        
    code, obj = MessageManager.get_sended_message_by_id_user(current_user.id, dt=today_dt)

    tomorrow = today_dt + timedelta(days=1) if today_dt is not None else None
    yesterday = today_dt - timedelta(days=1) if today_dt is not None else None
    day_view = today_dt is None

    return render_template(
        "mailbox.html",
        message_list=obj,
        tomorrow=tomorrow,
        yesterday=yesterday,
        day_view = not day_view,
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
        
    code, obj = MessageManager.get_received_message_by_id_user(current_user.id, dt=today_dt)

    tomorrow = today_dt + timedelta(days=1) if today_dt is not None else None
    yesterday = today_dt - timedelta(days=1) if today_dt is not None else None
    day_view = today_dt is None

    return render_template(
        "mailbox.html",
        message_list=obj,
        tomorrow=tomorrow,
        yesterday=yesterday,
        day_view = not day_view,
        list_type="received",
    )

@messages.route("/timeline", methods=["GET"])
@login_required
def get_timeline_month(_year, _month):

    _year = request.args.get('y',None)
    _month = request.args.get('m',None)

    first_day, number_of_days = calendar.monthrange(_year, _month)
    sent, received = number_of_days * [0], number_of_days * [0]

    message_list = MessageManager.get_timeline_month_mess_send(
        current_user.id, _month, _year
    )

    for elem in message_list:
        sent[elem.date_of_send.day - 1] += 1

    message_list = MessageManager.get_timeline_month_mess_received(
        current_user.id, _month, _year
    )

    for elem in message_list:
        received[elem.date_of_send.day - 1] += 1

    return render_template(
        "calendar_bs.html",
        calendar_view={
            "year": _year,
            "month": _month,
            "month_name": calendar.month_name[_month],
            "days_in_month": number_of_days,
            "starts_with": first_day,
            "sent": sent,
            "received": received,
        },
    )

