from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Email, Length

from app.utils.roles import Role
from app.models.ministry import Ministry


class UserCreateForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=80)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])

    role = SelectField(
        "Role",
        choices=[("", "—")] + [(r, Role.LABELS[r]) for r in Role.ALL],
        validators=[DataRequired()],
    )

    ministry_id = SelectField(
        "Ministry (only for Ministry Leaders)",
        coerce=lambda x: int(x) if x else None,
        validators=[Optional()],
    )

    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Create User")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ministry_id.choices = [("", "—")] + [
            (m.id, m.name) for m in Ministry.query.order_by(Ministry.name).all()
        ]


class UserEditForm(UserCreateForm):
    submit = SubmitField("Save Changes")