from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, BooleanField, SubmitField,
    DateField, RadioField,
)
from wtforms.validators import DataRequired, Optional, Email, Length

from app.utils.roles import Role
from app.models.ministry import Ministry
from app.models.member import Member
from app.models.family import Family


class UserCreateForm(FlaskForm):
    # ── Step 1: member identity ─────────────────────────────
    member_mode = RadioField(
        "Member",
        choices=[
            ("existing", "Link to existing member"),
            ("new", "Create a new member record"),
        ],
        default="existing",
    )
    existing_member_id = SelectField(
        "Existing Member",
        coerce=lambda x: int(x) if x else None,
        validators=[Optional()],
    )

    # ── New member fields (used when member_mode == "new") ──
    member_first_name = StringField("First Name", validators=[Optional(), Length(max=80)])
    member_last_name = StringField("Last Name", validators=[Optional(), Length(max=80)])
    member_gender = SelectField(
        "Gender",
        choices=[("", "—"), ("Male", "Male"), ("Female", "Female")],
        validators=[Optional()],
    )
    member_date_of_birth = DateField("Date of Birth", validators=[Optional()])
    member_phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    member_family_id = SelectField(
        "Church Family Group",
        coerce=lambda x: int(x) if x else None,
        validators=[Optional()],
    )

    # ── Step 2: staff account ───────────────────────────────
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
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
        # Only members that don't already have a user account
        self.existing_member_id.choices = [("", "— Select a member —")] + [
            (m.id, m.full_name)
            for m in Member.query.filter(Member.user_account == None)
                              .order_by(Member.last_name, Member.first_name).all()
        ]
        self.member_family_id.choices = [("", "—")] + [
            (f.id, f.name) for f in Family.query.order_by(Family.name).all()
        ]


class UserEditForm(FlaskForm):
    """Edit an existing user — name comes from the linked Member."""
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
    submit = SubmitField("Save Changes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ministry_id.choices = [("", "—")] + [
            (m.id, m.name) for m in Ministry.query.order_by(Ministry.name).all()
        ]