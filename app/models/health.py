from datetime import datetime
from app.extensions import db


class HealthArticle(db.Model):
    __tablename__ = "health_articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    summary = db.Column(db.String(500))
    body = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80))
    author_name = db.Column(db.String(120))

    cover_image_url = db.Column(db.String(500))
    cover_public_id = db.Column(db.String(300))

    is_published = db.Column(db.Boolean, default=False, nullable=False, index=True)
    published_at = db.Column(db.DateTime)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<HealthArticle {self.slug}>"