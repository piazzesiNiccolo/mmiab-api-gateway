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
