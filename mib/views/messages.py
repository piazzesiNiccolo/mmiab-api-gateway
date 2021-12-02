import datetime
from datetime import timedelta
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

@messages.route("/message/list/received", methods=["GET"])
@login_required
def mailbox_list_received():
    """
    Displays messages sent by current user
    :return: sent messages mailbox template
    """
    message_list = []
    if current_user.is_authenticated:
        code, obj = MessageManager.get_received_message_by_id_user(current_user.id)
    
    if code != 200:
        flash("Error while retriving the message")
        #TODO check return in case of failure
        #return redirect(url_for('mai'))
        #return mailbox


    return render_template(
        "mailbox.html",
        message_list=obj,
        list_type="received",
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

@messages.route("/message/list/sent?y=&m=&d=&", methods=["GET"])
@login_required
def timeline_daily_sent():

    year = request.args.get('y',None)
    month = request.args.get('m',None)
    day = request.args.get('d',None)

    today_dt = datetime(year, month, day)
    tomorrow = today_dt + timedelta(days=1)
    yesterday = today_dt - timedelta(days=1)

    messages = MessageManager.get_timeline_day_mess_send(
        current_user.id, year, month, day
    )


