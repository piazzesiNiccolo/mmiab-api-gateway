from .auth import auth
from .home import home
from .users import users
from .filters import filters
from .notifications import notifications
from .message import message

"""List of the views to be visible through the project
"""
blueprints = [home, auth, users, filters, notifications, message]
