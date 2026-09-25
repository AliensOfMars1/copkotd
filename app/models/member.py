from datetime import datetime, date
from app.extensions import db


class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)

    # ── Personal ─────────────────────────────────────────────
    title = db.Column(db.String(20))                    # Mr, Mrs, Dr, etc.
    first_name = db.Column(db.String(80), nullable=False)
    middle_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(10))                   # Male / Female
    date_of_birth = db.Column(db.Date)
    place_of_birth = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    marital_status = db.Column(db.String(20))           # Single, Married, etc.

    # ── Address ──────────────────────────────────────────────
    address_line1 = db.Column(db.String(200))
    gps_address = db.Column(db.String(50))
    hometown = db.Column(db.String(80))
    street_name = db.Column(db.String(120))
    city = db.Column(db.String(80))

    # ── Family ───────────────────────────────────────────────
    parent_name = db.Column(db.String(120))
    parent_relationship = db.Column(db.String(40))

    # ── Spiritual ────────────────────────────────────────────
    member_type = db.Column(db.String(80))              # free text for now
    holyghost_baptism = db.Column(db.Boolean, default=False)
    date_of_holy_spirit_baptism = db.Column(db.Date)
    water_baptism = db.Column(db.Boolean, default=False)
    date_of_baptism = db.Column(db.Date)
    date_of_conversion = db.Column(db.Date)
    date_of_joining_us = db.Column(db.Date)
    place_of_baptism = db.Column(db.String(120))
    officiating_minister_baptism = db.Column(db.String(120))
    officiating_ministers_district = db.Column(db.String(120))
    communicant = db.Column(db.Boolean, default=False)

    # ── Education / Work 
    occupation = db.Column(db.String(120))
    level_of_education = db.Column(db.String(120))

    # ── Dedication (for children) 
    dedicated = db.Column(db.Boolean, default=False)
    dedication_date = db.Column(db.Date)
    officiating_minister_dedication = db.Column(db.String(120))
    church_where_dedication_was_done = db.Column(db.String(120))

    # ── Status
    membership_status = db.Column(db.String(20), default="active", index=True)
    # active | inactive | transferred | backslider | deceased

    # ── Audit 
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Helpers
    @property
    def full_name(self):
        parts = [self.title, self.first_name, self.middle_name, self.last_name]
        return " ".join(p for p in parts if p)

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def age_group(self):
        """Matches EOY form categories."""
        a = self.age
        if a is None:
            return "unknown"
        if a < 13:
            return "child"          # Dedicated Children
        if a <= 19:
            return "teenager"
        if a <= 35:
            return "young_adult"
        return "other_adult"

    def __repr__(self):
        return f"<Member {self.full_name}>"