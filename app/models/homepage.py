from datetime import datetime
from app.extensions import db


class HomepageContent(db.Model):
    __tablename__ = "homepage_content"

    id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.String(40), nullable=False, index=True)
    # Values: 'event', 'announcement', 'sermon', 'service_time'

    title = db.Column(db.String(200))
    body = db.Column(db.Text)

    # Event-specific
    event_date = db.Column(db.Date)
    event_time = db.Column(db.String(40))
    location = db.Column(db.String(200))
    image_url = db.Column(db.String(500))  # Cloudinary URL

    # Sermon-specific
    speaker = db.Column(db.String(120))
    video_url = db.Column(db.String(500))

    # Service-time-specific
    service_name = db.Column(db.String(80))
    day_of_week = db.Column(db.String(20))
    start_time = db.Column(db.String(20))
    end_time = db.Column(db.String(20))

    # Scheduling
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    publish_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)

    # Ordering
    display_order = db.Column(db.Integer, default=0)

    # Audit
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_visible(self):
        """True if this content should appear on the public homepage right now."""
        from datetime import date
        now = datetime.utcnow()
        if not self.is_published:
            return False
        if self.publish_at and self.publish_at > now:
            return False
        if self.expires_at and self.expires_at < now:
            return False
        return True

    def __repr__(self):
        return f"<HomepageContent {self.content_type}: {self.title}>"