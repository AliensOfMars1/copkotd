from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class MinistryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    category = StringField("Category", validators=[Optional(), Length(max=80)])
    description = TextAreaField("Description", validators=[Optional()])
    meeting_day = StringField("Meeting Day", validators=[Optional(), Length(max=30)])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save Ministry")