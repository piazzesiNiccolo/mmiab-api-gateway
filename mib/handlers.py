from flask import flash
from flask import redirect
from flask import url_for


def page_404(e):  # pragma: no cover
    flash("404: Page Not Found")
    return redirect(url_for("home.index"))


def error_500(e):  # pragma: no cover
    flash("500: Internal Server Error")
    return redirect(url_for("home.index"))
