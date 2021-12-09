import pytest
from mib.validators.age import AgeValidator
from wtforms.validators import ValidationError
from mib.forms import UserForm
from datetime import datetime


class TestAgeValidator:
    @pytest.mark.parametrize(
        "min_age,max_age, ex_msg",
        [
            ("fail", 2, "min_age and max_age must be integers!"),
            (2, "fail", "min_age and max_age must be integers!"),
            (-3, 5, "min_age(-3) and max_age(5) must be positive!"),
            (3, -5, "min_age(3) and max_age(-5) must be positive!"),
            (10, 2, "max_age(2) must be greater than min_age(10)!"),
        ],
    )
    def test_constructor_value_error(self, min_age, max_age, ex_msg):
        with pytest.raises(ValueError) as e:
            AgeValidator(min_age=min_age, max_age=max_age)
            assert str(e) == ex_msg

    @pytest.mark.parametrize(
        "min_age, max_age", [(0, 0), (0, 60), (50, 100), (2, 80), (23, 71), (24, 25)]
    )
    def test_constructor_values_ok(self, min_age, max_age):
        m = AgeValidator(min_age, max_age)
        assert m.message == ""
        assert m.min_age == min_age
        assert m.max_age == max_age

    @pytest.mark.parametrize(
        "min_age,max_age,birthdate",
        [
            (0, 50, datetime.strptime("01/01/2000", "%d/%m/%Y")),
            (13, 0, datetime.strptime("01/01/1900", "%d/%m/%Y")),
            (18, 90, datetime.strptime("01/01/1996", "%d/%m/%Y")),
        ],
    )
    def test_call_validate_ok(self, min_age, max_age, birthdate):
        form = UserForm()
        form.birthdate.data = birthdate.date()
        m = AgeValidator(min_age, max_age)
        m(form, form.birthdate)
        assert m.message == ""

    @pytest.mark.parametrize(
        "min_age,max_age,birthdate,message",
        [
            (0, 50, datetime.strptime("01/01/1932", "%d/%m/%Y"), "You are too old!"),
            (13, 0, datetime.strptime("01/01/2012", "%d/%m/%Y"), "You are too young!"),
            (18, 90, datetime.strptime("01/01/1896", "%d/%m/%Y"), "You are too old!"),
            (15, 70, datetime.strptime("01/01/2010", "%d/%m/%Y"), "You are too young!"),
            (0, 0, None, "Invalid date"),
        ],
    )
    def test_call_validate_not_ok(self, min_age, max_age, birthdate, message):
        form = UserForm()
        if birthdate:
            form.birthdate.data = birthdate.date()
        with pytest.raises(ValidationError):
            m = AgeValidator(min_age, max_age)
            m(form, form.birthdate)
        assert m.message == message
