from datetime import datetime
from flask import Blueprint, render_template
from app.models.homepage import HomepageContent
from app.models.site_setting import SiteSetting
from app.utils.youtube import get_youtube_id, get_youtube_thumbnail

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    now = datetime.utcnow()

    # ── 1. Announcements (live, not expired) ────────────────
    announcements = (
        HomepageContent.query
        .filter_by(content_type="announcement", is_published=True)
        .filter((HomepageContent.expires_at == None) | (HomepageContent.expires_at > now))
        .order_by(HomepageContent.created_at.desc())
        .all()
    )

    # ── 2. Events (live, not expired, next 3 by date) ───────
    events = (
        HomepageContent.query
        .filter_by(content_type="event", is_published=True)
        .filter((HomepageContent.expires_at == None) | (HomepageContent.expires_at > now))
        .filter(HomepageContent.event_date >= now.date())
        .order_by(HomepageContent.event_date.asc())
        .limit(3)
        .all()
    )

    # ── 4. Service Times ────────────────────────────────────
    services = (
        HomepageContent.query
        .filter_by(content_type="service_time", is_published=True)
        .order_by(HomepageContent.display_order)
        .all()
    )

    # ── 5. Site Settings (Footer info) ──────────────────────
    settings = SiteSetting.as_dict()

    # ── 3. Latest Sermon ────────────────────────────────────
    current_sermon = (
        HomepageContent.query
        .filter_by(content_type="sermon", is_published=True)
        .order_by(HomepageContent.created_at.desc())
        .first()
    )

    # Extract YouTube details if a sermon exists
    sermon_video_id = get_youtube_id(current_sermon.video_url) if current_sermon and current_sermon.video_url else None
    sermon_thumbnail = get_youtube_thumbnail(current_sermon.video_url) if current_sermon and current_sermon.video_url else None


    return render_template(
        "public/index.html",
        announcements=announcements,
        events=events,
        current_sermon=current_sermon,
        sermon_video_id=sermon_video_id,
        sermon_thumbnail=sermon_thumbnail,
        services=services,
        settings=settings,
    )
    