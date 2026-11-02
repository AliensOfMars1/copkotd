from flask import Blueprint, render_template
from app.models.gallery import GalleryPhoto

gallery_bp = Blueprint("gallery", __name__)


@gallery_bp.route("/gallery")
def gallery():
    photos = (
        GalleryPhoto.query
        .filter_by(is_published=True)
        .order_by(GalleryPhoto.display_order, GalleryPhoto.created_at.desc())
        .all()
    )
    return render_template("public/gallery.html", photos=photos)