from datetime import datetime
from app.extensions import db


class GalleryPhoto(db.Model):
    __tablename__ = "gallery_photos"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(300))  # Cloudinary public_id for deletion
    display_order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<GalleryPhoto {self.id}: {self.title or 'untitled'}>"