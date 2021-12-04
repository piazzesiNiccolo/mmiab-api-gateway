from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask.json import jsonify
from flask_login import login_required
from mib.rao.notification_manager import NotificationManager


notifications = Blueprint('notifications', __name__)

@notifications.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    code, data = NotificationManager.get_notifications()
    print('status_code:', code)
    if code == 200:
        return {
            "status_code" : 200,
            "status" : "success",
            "data" : data,
        }
    else:
        return {
            "status_code" : 500,
            "status" : "failed",
            "message" : "Unexpected reponse from user microservice"
            }

@notifications.route('/notifications/add', methods=['POST'])
def add_notifications():
    code = NotificationManager.add_notifications(request.args.get("data", None))
    print('status_code:', code)
    if code == 200:
        return {
            "status_code" : 200,
            "status" : "success",
        }
    else:
        return {
            "status_code" : 500,
            "status" : "failed",
            "message" : "Unexpected reponse from user microservice"
            }
