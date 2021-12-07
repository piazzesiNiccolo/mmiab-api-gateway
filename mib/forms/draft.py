import wtforms as f
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_wtf.file import FileField
from flask_wtf.file import FileSize
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import InputRequired
from wtforms.validators import Optional
from wtforms.fields.html5 import DateTimeLocalField

_MAX_CONTENT_LENGTH = 16 * 1024 * 1024

_ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]

delivery_format = "%H:%M %d/%m/%Y"

class RecipientForm(FlaskForm):
    recipient = f.SelectField("Recipient", default=[])
    search = f.StringField("Search Users", default="")

class EditMessageForm(FlaskForm):
    message_body = f.TextAreaField("Message", validators=[InputRequired()])
    delivery_date = DateTimeLocalField(
        "Delivery Date", format='%Y-%m-%dT%H:%M', validators=[Optional()]
    )
    recipients = f.FieldList(f.FormField(RecipientForm))
    display = ["message_body", "delivery_date", "recipients"]
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
    display = ["message_body", "image", "delivery_date", "recipients"]
