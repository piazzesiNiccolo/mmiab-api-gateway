from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for
from flask.helpers import flash
from flask_login import current_user
from flask_login import login_required
from flask.globals import request
from mib.rao.lottery_manager import LotteryManager
from mib.forms.lottery import LotteryForm

from calendar import monthrange
from datetime import date
from datetime import timedelta


def next_lottery_date():

    # this should probably be a request to lottery in a real environment
    days_in_month = lambda dt: monthrange(dt.year, dt.month)[1]
    today = date.today()
    first_day = today.replace(day=1) + timedelta(days_in_month(today))
    return first_day.strftime("%d/%m/%Y")

lottery = Blueprint('lottery', __name__)

@lottery.route("/lottery/participate", methods=["GET", "POST"])
@login_required
def participate():
    """
    Get the user choice for the next lottery
    """
    form = LotteryForm()

    code, choice = LotteryManager.get_participant(current_user.get_id())
    if code == 404:
        if request.method == "POST":
            if form.validate_on_submit():
                code, obj = LotteryManager.add_participant(
                    id=current_user.get_id(), choice=form.choice.data
                )
                if code == 201:
                    return render_template(
                        "lottery.html",
                        date=next_lottery_date(),
                        is_participating=True,
                        choice=form.choice.data,
                    )
                else: #we assume that calling add_participant from here can't return 200
                    flash(obj)
                    return render_template(
                    "lottery.html",
                    date=next_lottery_date(),
                    is_participating=False,
                    form=form,
                )
        return render_template(
                    "lottery.html",
                    date=next_lottery_date(),
                    is_participating=False,
                    form=form,
                )
    elif code == 500:
        flash(choice)
        return render_template(
                    "lottery.html",
                    date=next_lottery_date(),
                    is_participating=False,
                    form=form,
                )
    else:
        return render_template(
            "lottery.html",
            form=form,
            date=next_lottery_date(),
            is_participating=True,
            choice=choice
        )

@lottery.route("/lottery", methods=["GET"])
@login_required
def next_lottery():
    """
    Displays the date of the next lottery, and shows user choice
    if it's present
    """
    code, choice = LotteryManager.get_participant(current_user.get_id())
    if code == 200:
        return render_template(
            "lottery.html",
            date=next_lottery_date(),
            is_participating=True,
            choice=choice,
        )
    elif code == 404:
        return redirect(url_for("lottery.participate"))
    else:
        flash(choice) # a bit confusing maybe, but choice becomes an error message when a timeout occurs
        return redirect(url_for("lottery.participate"))
