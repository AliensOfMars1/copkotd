from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional, Length

from app.models.user import User


class FamilyForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    description = TextAreaField("Description", validators=[Optional()])
    leader_id = SelectField(
        "Family Leader (optional)",
        coerce=lambda x: int(x) if x else None,
        validators=[Optional()],
    )
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save Family")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.leader_id.choices = [("", "—")] + [
            (u.id, u.full_name) for u in User.query.order_by(User.first_name).all()
        ]