import wtforms as f
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_wtf.file import FileField
from flask_wtf.file import FileSize
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import InputRequired
from wtforms.validators import Optional

_MAX_CONTENT_LENGTH = 16 * 1024 * 1024

_ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]

class RecipientForm(FlaskForm):
    recipient = f.SelectField("Recipient", default=[])
    search = f.StringField("Search Users", default="")

class EditMessageForm(FlaskForm):
    body_message = f.TextAreaField("Message", validators=[InputRequired()])
    date_of_send = f.DateTimeField(
        "Delivery Date", format=delivery_format, validators=[Optional()]
    )
    recipients = f.FieldList(f.FormField(RecipientForm))
    display = ["body_message", "date_of_send", "recipients"]
    image = FileField(
        validators=[
            FileAllowed(
                _ALLOWED_EXTENSIONS,
                message="You can only upload .jpg, .jpeg or .png files",
            ),
            Optional(),
            FileSize(max_size=_MAX_CONTENT_LENGTH, message="max size allowed=16 MB"),
        ]
    )
    display = ["body_message", "image", "date_of_send", "recipients"]