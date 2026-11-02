from datetime import datetime
from app.extensions import db


class Ministry(db.Model):
    __tablename__ = "ministries"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    category = db.Column(db.String(80))
    description = db.Column(db.Text)
    meeting_day = db.Column(db.String(30))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    leaders = db.relationship(
        "User",
        backref="ministry",
        lazy="dynamic",
        foreign_keys="User.ministry_id",
    )

    @property
    def leader_count(self):
        return self.leaders.count()

    def __repr__(self):
        return f"<Ministry {self.name}>"