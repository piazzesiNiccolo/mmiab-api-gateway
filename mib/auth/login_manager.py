from flask_login import LoginManager
from mib.rao.user_manager import UserManager


def init_login_manager(app):
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"
    login_manager.refresh_view = "auth.re_login"

    @login_manager.user_loader
    def load_user(user_id):  # pragma: no cover
        """
        We need to connect to users endpoint and load the user.
        Here we can implement the redis caching

        :param user_id: user id
        :return: the user object
        """
        user, _ = UserManager.get_user_by_id(user_id, cache_propic=True)
        if user is not None:
            user.authenticated = True
        return user

    return login_manager
