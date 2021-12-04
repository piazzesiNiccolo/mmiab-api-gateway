from .auth import auth
from .home import home
from .users import users
from .filters import filters
from .notifications import notifications
from .messages import messages

"""List of the views to be visible through the project
"""
blueprints = [home, auth, users, filters, notifications, messages]
