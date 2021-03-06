import wtforms as f
from mib import app
from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField
from wtforms.fields.html5 import DateField
from wtforms.fields.html5 import TelField
from flask_wtf.file import FileField
from flask_wtf.file import FileAllowed
from flask_wtf.file import FileSize
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import Length
from wtforms.validators import Optional


from mib.validators.age import AgeValidator


class UserForm(FlaskForm):
    """Form created to allow the customers sign up to the application.
    This form requires all the personal information, in order to create the account.
    """

    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    first_name = f.StringField("First Name", validators=[DataRequired()])
    last_name = f.StringField("Last Name", validators=[DataRequired()])
    password = f.PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(
                min=5, max=127, message="Password must be between 5 and 127 characters"
            ),
        ],
    )
    # birthdate = DateField('Birthdate', format="%d/%m/%Y", validators=[AgeValidator(min_age=13)])
    birthdate = DateField("Birthdate", validators=[AgeValidator(min_age=13)])
    nickname = f.StringField("Nickname", validators=[Optional()])
    location = f.StringField("Location", validators=[Optional()])
    profile_picture = FileField(
        "Profile Picture",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png"],
                message="You can only upload a jpg,jpeg, or png file",
            ),
            Optional(),
            FileSize(max_size=16 * 1024 * 1024, message="max size allowed=16 MB"),
        ],
    )
    phone = TelField(
        "Phone",
        validators=[
            DataRequired(),
            Length(
                min=10, max=25, message="Phone number must be between 10 and 25 digits"
            ),
        ],
    )

    display = [
        "email",
        "first_name",
        "last_name",
        "nickname",
        "location",
        "profile_picture",
        "password",
        "birthdate",
        "phone",
    ]


class EditProfileForm(UserForm):
    password = f.PasswordField("Password", validators=[Optional()])
    old_password = f.PasswordField("Old Password", validators=[Optional()])
    new_password = f.PasswordField("New Password", validators=[Optional()])
    UserForm.display.extend(["new_password", "old_password"])
