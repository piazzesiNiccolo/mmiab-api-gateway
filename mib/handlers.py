from flask import render_template


def page_404(e): # pragma: no cover
    return render_template('404.html'), 404


def error_500(e): # pragma: no cover
    return render_template('500.html'), 500
