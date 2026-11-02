from datetime import datetime
from flask import Blueprint, render_template
from app.models.homepage import HomepageContent

announcements_bp = Blueprint("announcements", __name__)


@announcements_bp.route("/announcements")
def announcements():
    now = datetime.utcnow()
    items = (
        HomepageContent.query
        .filter_by(content_type="announcement", is_published=True)
        .filter((HomepageContent.expires_at == None) | (HomepageContent.expires_at > now))
        .order_by(HomepageContent.created_at.desc())
        .all()
    )
    return render_template(
        "public/announcements.html",
        announcements=items,
        now=now,
    )