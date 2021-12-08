from flask_wtf import FlaskForm
import wtforms as f
from wtforms.validators import DataRequired, NumberRange

class LotteryForm(FlaskForm):
    choice = f.IntegerField(
        label="choice", validators=[DataRequired(), NumberRange(min=1, max=50)]
    )