from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt
from app.utils.roles import Role


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(30))
    role = db.Column(db.String(40), nullable=False, default=Role.MINISTRY_LEADER)
    ministry_id = db.Column(db.Integer, db.ForeignKey("ministries.id"), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Link to Member record ───────────────────────────────
    member_id = db.Column(
        db.Integer,
        db.ForeignKey("members.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )
    member = db.relationship(
        "Member",
        backref=db.backref("user_account", uselist=False),
        foreign_keys=[member_id],
        uselist=False,
    )

    def set_password(self, raw):
        self.password_hash = bcrypt.generate_password_hash(raw).decode("utf-8")

    def check_password(self, raw):
        return bcrypt.check_password_hash(self.password_hash, raw)

    @property
    def full_name(self):
        """Display name — Member is source of truth when linked."""
        if self.member:
            return self.member.full_name
        return f"{self.first_name} {self.last_name}"

    @property
    def role_label(self):
        return Role.LABELS.get(self.role, self.role)

    @property
    def role_icon(self):
        _ICONS = {
            Role.SUPER_ADMIN: "bi-shield-lock-fill",
            Role.ADMIN: "bi-person-gear",
            Role.FINANCIAL_OFFICER: "bi-cash-coin",
            Role.RECORDS_OFFICER: "bi-folder-symlink-fill",
            Role.COMPLIANCE_OFFICER: "bi-clipboard-check-fill",
            Role.DATA_OFFICER: "bi-bar-chart-fill",
            Role.COMMUNICATIONS_OFFICER: "bi-megaphone-fill",
            Role.PROGRAMS_OFFICER: "bi-calendar-event-fill",
            Role.MINISTRY_LEADER: "bi-people-fill",
            Role.HEALTH_OFFICER: "bi-heart-pulse-fill",
        }
        return _ICONS.get(self.role, "bi-person-badge-fill")

    def has_role(self, *roles):
        return self.role in roles

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"