from flask_login import login_manager
from flask_login.mixins import AnonymousUserMixin
import pytest
import mock
from flask import current_app
from flask_login import login_user
from mib.auth.user import User
from mib.auth.login_manager import init_login_manager


class TestLoginManager:
    @pytest.mark.parametrize(
        "user",
        [
            None,
            User(
                id=1,
                email="email@email.com",
                is_active=False,
                authenticated=False,
                is_anonymous=False,
                extra="",
            ),
        ],
    )
    def test_init_login_manager(self, user):
        with mock.patch("mib.rao.user_manager.UserManager.get_user_by_id") as m:
            m.return_value = user, None
            mgr = init_login_manager(current_app)
            assert mgr.login_view == "auth.login"
            assert mgr.refresh_view == "auth.re_login"
            mgr.user_loader(1)
