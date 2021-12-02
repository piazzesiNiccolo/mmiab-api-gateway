from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_login import login_required
from mib.rao.notification_manager import NotificationManager


notifications = Blueprint('notifications', __name__)

@notifications.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    NotificationManager.get_notifications()
    return redirect(url_for('users.user_profile'))

