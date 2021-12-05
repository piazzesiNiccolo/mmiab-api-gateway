from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for
from flask_login import current_user

home = Blueprint('home', __name__)


@home.route('/', methods=['GET', 'POST'])
def index():
    """General route for the index page
    """
    if current_user.is_authenticated:
        return redirect(url_for("messages.list_received_messages"))

    return render_template("index.html")

