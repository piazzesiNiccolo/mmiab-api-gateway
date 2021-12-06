from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask.json import jsonify
from flask_login import login_required
from flask_login import current_user
from mib.rao.notification_manager import NotificationManager


notifications = Blueprint('notifications', __name__)

@notifications.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    code, data = NotificationManager.get_notifications(current_user.id)
    print('status_code:', code)
    if code == 200:
        return jsonify(notifications={
            "status_code" : 200,
            "status" : "success",
            "data" : data,
        })
    else:
        return jsonify(notifications={
            "status_code" : 500,
            "status" : "failed",
            "message" : "Unexpected reponse from user microservice"
            })

