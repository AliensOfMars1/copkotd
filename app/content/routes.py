from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.auth.decorators import role_required
from app.utils.roles import Role
from app.models.homepage import HomepageContent
from app.content.forms import AnnouncementForm, EventForm
from datetime import datetime
from app.utils.cloudinary import upload_image, delete_image
from app.content.forms import AnnouncementForm, EventForm, SermonForm, ServiceTimeForm

content_bp = Blueprint("content", __name__, url_prefix="/content")

ALLOWED_ROLES = (Role.SUPER_ADMIN, Role.ADMIN, Role.COMMUNICATIONS_OFFICER)

@content_bp.route("/")
@login_required
@role_required(*ALLOWED_ROLES)
def dashboard():
    announcements = HomepageContent.query.filter_by(content_type="announcement").order_by(HomepageContent.created_at.desc()).all()
    events = HomepageContent.query.filter_by(content_type="event").order_by(HomepageContent.event_date.asc()).all()
    
    # Fetch the latest sermon
    current_sermon = HomepageContent.query.filter_by(content_type="sermon").order_by(HomepageContent.created_at.desc()).first()
    
    # Fetch all service times
    services = HomepageContent.query.filter_by(content_type="service_time").order_by(HomepageContent.display_order).all()
    
    return render_template(
        "content/dashboard.html",
        announcements=announcements,
        events=events,
        current_sermon=current_sermon,
        services=services,
        now=datetime.utcnow(),
    )

# ── ANNOUNCEMENTS ──────────────────────────────────────────

@content_bp.route("/announcements/new", methods=["GET", "POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def create_announcement():
    form = AnnouncementForm()
    if form.validate_on_submit():
        # If a date is set, expire at 00:00 on that day
        expires_at = None
        if form.expires_date.data:
            expires_at = datetime.combine(form.expires_date.data, datetime.min.time())

        content = HomepageContent(
            content_type="announcement",
            title=form.title.data.strip(),
            body=form.body.data.strip(),
            is_published=form.is_published.data,
            expires_at=expires_at,
            created_by=current_user.id,
            updated_by=current_user.id,
        )
        db.session.add(content)
        db.session.commit()
        flash("Announcement created successfully.", "success")
        return redirect(url_for("content.dashboard"))
    return render_template("content/announcement_form.html", form=form, announcement=None)

@content_bp.route("/announcements/<int:id>/edit", methods=["GET", "POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def edit_announcement(id):
    content = HomepageContent.query.get_or_404(id)
    form = AnnouncementForm(obj=content)

    if form.validate_on_submit():
        content.title = form.title.data.strip()
        content.body = form.body.data.strip()
        content.is_published = form.is_published.data

        # If a date is set, expire at 00:00 on that day
        if form.expires_date.data:
            content.expires_at = datetime.combine(form.expires_date.data, datetime.min.time())
        else:
            content.expires_at = None

        content.updated_by = current_user.id
        db.session.commit()
        flash("Announcement updated.", "success")
        return redirect(url_for("content.dashboard"))

    # Pre-fill date field from existing expires_at (if any)
    if content.expires_at:
        form.expires_date.data = content.expires_at.date()

    return render_template("content/announcement_form.html", form=form, announcement=content)

@content_bp.route("/announcements/<int:id>/delete", methods=["POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def delete_announcement(id):
    content = HomepageContent.query.get_or_404(id)
    db.session.delete(content)
    db.session.commit()
    flash("Announcement deleted.", "info")
    return redirect(url_for("content.dashboard"))

# ── EVENTS ──────────────────────────────────────────────────

@content_bp.route("/events/new", methods=["GET", "POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        # Handle image upload
        image_url = None
        if form.image.data and form.image.data.filename:
            try:
                result = upload_image(form.image.data, folder="kotd/events")
                image_url = result["url"]
            except Exception as e:
                flash(f"Image upload failed: {e}", "warning")

        # Handle expiry date
        expires_at = None
        if form.expires_date.data:
            expires_at = datetime.combine(form.expires_date.data, datetime.min.time())

        event = HomepageContent(
            content_type="event",
            title=form.title.data.strip(),
            body=form.body.data.strip(),
            event_date=form.event_date.data,
            event_time=form.event_time.data,
            location=form.location.data,
            image_url=image_url,
            is_published=form.is_published.data,
            expires_at=expires_at,
            created_by=current_user.id,
            updated_by=current_user.id,
        )
        db.session.add(event)
        db.session.commit()
        flash("Event created successfully.", "success")
        return redirect(url_for("content.dashboard"))
        
    return render_template("content/event_form.html", form=form, event=None)


@content_bp.route("/events/<int:id>/edit", methods=["GET", "POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def edit_event(id):
    event = HomepageContent.query.get_or_404(id)
    form = EventForm(obj=event)
    
    if form.validate_on_submit():
        event.title = form.title.data.strip()
        event.body = form.body.data.strip()
        event.event_date = form.event_date.data
        event.event_time = form.event_time.data
        event.location = form.location.data
        event.is_published = form.is_published.data

        # Replace image if a new one is uploaded
        if form.image.data and form.image.data.filename:
            try:
                # Delete old one (best-effort)
                if event.image_url:
                    try:
                        old_public_id = event.image_url.split("/upload/")[1].split("/", 1)[1].rsplit(".", 1)[0]
                        delete_image(old_public_id)
                    except Exception:
                        pass  # skip deletion if extraction fails
                
                result = upload_image(form.image.data, folder="kotd/events")
                event.image_url = result["url"]
            except Exception as e:
                flash(f"Image upload failed: {e}", "warning")

        # Handle expiry
        if form.expires_date.data:
            event.expires_at = datetime.combine(form.expires_date.data, datetime.min.time())
        else:
            event.expires_at = None

        event.updated_by = current_user.id
        db.session.commit()
        flash("Event updated.", "success")
        return redirect(url_for("content.dashboard"))

    # Pre-fill date picker
    if event.expires_at:
        form.expires_date.data = event.expires_at.date()

    return render_template("content/event_form.html", form=form, event=event)


@content_bp.route("/events/<int:id>/delete", methods=["POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def delete_event(id):
    event = HomepageContent.query.get_or_404(id)
    
    # Delete image from Cloudinary (best-effort)
    if event.image_url:
        try:
            public_id = event.image_url.split("/upload/")[1].split("/", 1)[1].rsplit(".", 1)[0]
            delete_image(public_id)
        except Exception:
            pass
    
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted.", "info")
    return redirect(url_for("content.dashboard"))


# ── SERMON ──────────────────────────────────────────────────

@content_bp.route("/sermon", methods=["GET", "POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def edit_sermon():
    # Get the latest sermon if it exists
    sermon = HomepageContent.query.filter_by(content_type="sermon").order_by(HomepageContent.created_at.desc()).first()
    form = SermonForm(obj=sermon)
    
    if form.validate_on_submit():
        if not sermon:
            # Create first sermon
            sermon = HomepageContent(content_type="sermon", created_by=current_user.id)
            db.session.add(sermon)
            
        sermon.title = form.title.data.strip()
        sermon.speaker = form.speaker.data.strip()
        sermon.body = form.body.data.strip()
        sermon.event_date = form.event_date.data
        sermon.video_url = form.video_url.data.strip()
        sermon.is_published = True
        sermon.updated_by = current_user.id
        
        db.session.commit()
        flash("Latest sermon updated.", "success")
        return redirect(url_for("content.dashboard"))
        
    return render_template("content/sermon_form.html", form=form, sermon=sermon)


# ── SERVICE TIMES ───────────────────────────────────────────

@content_bp.route("/services", methods=["GET", "POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def manage_services():
    services = HomepageContent.query.filter_by(content_type="service_time").order_by(HomepageContent.display_order).all()
    return render_template("content/services_list.html", services=services)


@content_bp.route("/services/new", methods=["GET", "POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def create_service():
    form = ServiceTimeForm()
    if form.validate_on_submit():
        # Determine display order (append to end)
        count = HomepageContent.query.filter_by(content_type="service_time").count()
        
        service = HomepageContent(
            content_type="service_time",
            service_name=form.service_name.data.strip(),
            day_of_week=form.day_of_week.data.strip(),
            start_time=form.start_time.data.strip(),
            end_time=form.end_time.data.strip(),
            display_order=count + 1,
            is_published=True,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(service)
        db.session.commit()
        flash("Service time added.", "success")
        return redirect(url_for("content.manage_services"))
    return render_template("content/service_form.html", form=form, service=None)


@content_bp.route("/services/<int:id>/edit", methods=["GET", "POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def edit_service(id):
    service = HomepageContent.query.get_or_404(id)
    form = ServiceTimeForm(obj=service)
    if form.validate_on_submit():
        service.service_name = form.service_name.data.strip()
        service.day_of_week = form.day_of_week.data.strip()
        service.start_time = form.start_time.data.strip()
        service.end_time = form.end_time.data.strip()
        service.updated_by = current_user.id
        db.session.commit()
        flash("Service time updated.", "success")
        return redirect(url_for("content.manage_services"))
    return render_template("content/service_form.html", form=form, service=service)


@content_bp.route("/services/<int:id>/delete", methods=["POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def delete_service(id):
    service = HomepageContent.query.get_or_404(id)
    db.session.delete(service)
    db.session.commit()
    flash("Service time removed.", "info")
    return redirect(url_for("content.manage_services"))