from flask_wtf import FlaskForm
from wtforms import (
    StringField, DateField, SelectField, BooleanField, TextAreaField, SubmitField
)
from wtforms.validators import DataRequired, Optional, Email, Length


class MemberForm(FlaskForm):
    # ── Personal ─────────────────────────────────────────────
    title = SelectField(
        "Title",
        choices=[("", "—"),
                 ("Apostle", "Apostle"),
                 ("Prophet", "Prophet"),
                 ("Evangelist", "Evangelist"),
                 ("Pastor", "Pastor"),
                 ("Overseer", "Overseer"),
                 ("Elder", "Elder"),
                 ("Deacon", "Deacon"),
                 ("Deaconess", "Deaconess"),
                 ("Mr.", "Mr."),
                 ("Mrs.", "Mrs."),
                 ("Miss", "Miss"),
                 ("Dr.", "Dr."),
                 ("Prof.", "Prof.")],
        validators=[Optional()],
    )
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=80)])
    middle_name = StringField("Middle Name", validators=[Optional(), Length(max=80)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=80)])
    gender = SelectField(
        "Gender",
        choices=[("", "—"), ("Male", "Male"), ("Female", "Female")],
        validators=[Optional()],
    )
    date_of_birth = DateField("Date of Birth", validators=[Optional()])
    place_of_birth = StringField("Place of Birth", validators=[Optional(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    marital_status = SelectField(
        "Marital Status",
        choices=[("", "—"), ("Single", "Single"), ("Married", "Married"),
                 ("Widowed", "Widowed"), ("Divorced", "Divorced")],
        validators=[Optional()],
    )

    # ── Address ──────────────────────────────────────────────
    address_line1 = StringField("Address Line 1", validators=[Optional(), Length(max=200)])
    gps_address = StringField("GPS Address", validators=[Optional(), Length(max=50)])
    hometown = StringField("Hometown", validators=[Optional(), Length(max=80)])
    street_name = StringField("Street Name", validators=[Optional(), Length(max=120)])
    city = StringField("City", validators=[Optional(), Length(max=80)])

    # ── Family ───────────────────────────────────────────────
    parent_name = StringField("Parent Name", validators=[Optional(), Length(max=120)])
    parent_relationship = StringField("Parent Relationship", validators=[Optional(), Length(max=40)])

    # ── Spiritual ────────────────────────────────────────────
    member_type = SelectField(
        "Member Type",
        choices=[("", "—"),
                 ("Member", "Member"),
                 ("New Convert", "New Convert"),
                 ("New Member", "New Member"),
                 ("Officer", "Officer"),
                 ("Minister", "Minister")],
        validators=[Optional()],
    )
    holyghost_baptism = BooleanField("Holy Ghost Baptism")
    date_of_holy_spirit_baptism = DateField("Date of Holy Spirit Baptism", validators=[Optional()])
    water_baptism = BooleanField("Water Baptism")
    date_of_baptism = DateField("Date of Baptism", validators=[Optional()])
    date_of_conversion = DateField("Date of Conversion", validators=[Optional()])
    date_of_joining_us = DateField("Date of Joining Us", validators=[Optional()])
    place_of_baptism = StringField("Place of Baptism", validators=[Optional(), Length(max=120)])
    officiating_minister_baptism = StringField("Officiating Minister (Baptism)", validators=[Optional(), Length(max=120)])
    officiating_ministers_district = StringField("Officiating Minister's District/Church", validators=[Optional(), Length(max=120)])
    communicant = BooleanField("Communicant")

    # ── Education / Work ─────────────────────────────────────
    occupation = SelectField(
        "Occupation",
        choices=[("", "—"),
                 ("Student", "Student"),
                 ("Teacher", "Teacher"),
                 ("Doctor", "Doctor"),
                 ("Nurse", "Nurse"),
                 ("Engineer", "Engineer"),
                 ("Accountant", "Accountant"),
                 ("Police Officer", "Police Officer"),
                 ("Firefighter", "Firefighter"),
                 ("Chef", "Chef"),
                 ("Waiter/Waitress", "Waiter/Waitress"),
                 ("Farmer", "Farmer"),
                 ("Carpenter", "Carpenter"),
                 ("Electrician", "Electrician"),
                 ("Librarian", "Librarian"),
                 ("Retail Salesperson", "Retail Salesperson"),
                 ("Cashier", "Cashier"),
                 ("Receptionist", "Receptionist"),
                 ("Janitor/Cleaner", "Janitor/Cleaner"),
                 ("Driver", "Driver"),
                 ("Mechanic", "Mechanic"),
                 ("Others", "Others")],
        validators=[Optional()],
    )
    level_of_education = SelectField(
        "Level of Education",
        choices=[("", "—"),
                 ("None", "None"),
                 ("Basic", "Basic"),
                 ("Secondary", "Secondary"),
                 ("Vocational/Technical", "Vocational/Technical"),
                 ("Professional Certification", "Professional Certification"),
                 ("Diploma", "Diploma"),
                 ("Bachelor or Equivalent", "Bachelor or Equivalent"),
                 ("Masters or Equivalent", "Masters or Equivalent"),
                 ("Doctoral or Equivalent", "Doctoral or Equivalent")],
        validators=[Optional()],
    )

    # ── Dedication ───────────────────────────────────────────
    dedicated = BooleanField("Dedicated")
    dedication_date = DateField("Dedication Date", validators=[Optional()])
    officiating_minister_dedication = StringField("Officiating Minister (Dedication)", validators=[Optional(), Length(max=120)])
    church_where_dedication_was_done = StringField("Church Where Dedication Was Done", validators=[Optional(), Length(max=120)])

    # ── Status ───────────────────────────────────────────────
    membership_status = SelectField(
        "Membership Status",
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("transferred", "Transferred"),
            ("backslider", "Backslider"),
            ("deceased", "Deceased"),
        ],
        default="active",
        validators=[DataRequired()],
    )

    submit = SubmitField("Save Member")