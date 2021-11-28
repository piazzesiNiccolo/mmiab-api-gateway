from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_login import (login_user, login_required)
from flask_login import current_user

from typing import Text

from mib.rao.message_manager import MessageManager
from mib.auth.user import User

messages = Blueprint('messages', __name__)


@messages.route("/read_message/<int:id>", methods=["GET"])
@login_required
def read_messages(id):

    """
    Let the user read the selected message
    """

    response = MessageManager.read_message(id)
    if response.status_code != 200:
        flash("Error while retraiving the message")
        #check return
        #return redirect(url_for('mai'))
        #return mailbox 
    
    return render_template('read_message.html', message=response)