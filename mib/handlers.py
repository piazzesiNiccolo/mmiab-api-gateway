import flask
from flask import flash
from flask import redirect
from flask import url_for


def page_404(e):  # pragma: no cover
    err = "404: Page Not Found"
    if err not in flask.get_flashed_messages():
        flash(err)
    return redirect(url_for("home.index"))


def error_500(e):  # pragma: no cover
    err = "500: Internal Server Error"
    if err not in flask.get_flashed_messages():
        flash(err)
    return redirect(url_for("home.index"))
