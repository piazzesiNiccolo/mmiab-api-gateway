from mib.auth.user import User
import pytest


class TestAuthUser:
    @pytest.mark.parametrize("id", [1, 2])
    @pytest.mark.parametrize("email", [f"email{i}@email{i}.com" for i in range(2)])
    @pytest.mark.parametrize("is_active", [True, False])
    @pytest.mark.parametrize("authenticated", [True, False])
    @pytest.mark.parametrize("is_anonymous", [True, False])
    def test_build_from_json(self, id, email, is_active, authenticated, is_anonymous):
        usr = User.build_from_json(
            {
                "id": id,
                "email": email,
                "is_active": is_active,
                "authenticated": authenticated,
                "is_anonymous": is_anonymous,
                "extra": {},
            }
        )
        assert usr.get_id() == id
        assert usr.email == email
        assert usr.is_active == is_active
        assert usr.is_authenticated == authenticated
        assert usr.is_anonymous == is_anonymous

    @pytest.mark.parametrize("id", [1, 2])
    @pytest.mark.parametrize("email", [f"email{i}@email{i}.com" for i in range(2)])
    @pytest.mark.parametrize("is_active", [True, False])
    @pytest.mark.parametrize("authenticated", [True, False])
    @pytest.mark.parametrize("is_anonymous", [True, False])
    def test_init_user(self, id, email, is_active, authenticated, is_anonymous):
        usr = User(
            id=id,
            email=email,
            is_active=is_active,
            authenticated=authenticated,
            is_anonymous=is_anonymous,
            extra={"extra1": 1, "email": email},
        )
        assert usr.id == id
        assert usr.email == email
        assert usr.is_active == is_active
        assert usr.authenticated == authenticated
        assert usr.is_anonymous == is_anonymous
        assert usr.extra_data["extra1"] == 1

    @pytest.mark.parametrize("kw,val", [("email", "foo"), ("extra1", 1)])
    def test_get_kw_ok(self, kw, val):
        usr = User(
            id=1,
            email="foo",
            is_active=True,
            authenticated=False,
            is_anonymous=False,
            extra={"extra1": 1},
        )
        assert usr.__getattr__(kw) == val

    def test_get_kw_err(self):
        usr = User(
            id=1,
            email="foo",
            is_active=True,
            authenticated=False,
            is_anonymous=False,
            extra={"extra1": 1},
        )
        with pytest.raises(AttributeError):
            usr.__getattr__("fail")

    def test_str_user(self):
        usr = User(
            id=1,
            email="foo",
            is_active=True,
            authenticated=False,
            is_anonymous=False,
            extra={},
        )
        s = str(usr)
        assert (
            s
            == "User Object\nid=1\nemail=foo\nis_active=True\nauthenticated=False\nis_anonymous=False\nextra_data={}\n"
        )
