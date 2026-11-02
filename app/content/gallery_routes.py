from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.auth.decorators import role_required
from app.utils.roles import Role
from app.models.gallery import GalleryPhoto
from app.utils.cloudinary import upload_image, delete_image


gallery_admin_bp = Blueprint("gallery_admin", __name__, url_prefix="/content/gallery")

ALLOWED_ROLES = (Role.SUPER_ADMIN, Role.ADMIN, Role.COMMUNICATIONS_OFFICER)


@gallery_admin_bp.route("/")
@login_required
@role_required(*ALLOWED_ROLES)
def list_photos():
    photos = GalleryPhoto.query.order_by(GalleryPhoto.display_order, GalleryPhoto.created_at.desc()).all()
    return render_template("content/gallery_list.html", photos=photos)


# ── Old bulk endpoint (still works if you ever use form submit) ──
@gallery_admin_bp.route("/upload", methods=["POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def upload_photo():
    files = request.files.getlist("photos")
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    count = 0
    for f in files:
        if f and f.filename:
            try:
                result = upload_image(f, folder="kotd/gallery")
                photo = GalleryPhoto(
                    title=title,
                    description=description,
                    image_url=result["url"],
                    public_id=result["public_id"],
                    created_by=current_user.id,
                )
                db.session.add(photo)
                count += 1
            except Exception as e:
                flash(f"Upload failed for {f.filename}: {e}", "danger")

    if count:
        db.session.commit()
        flash(f"{count} photo(s) uploaded.", "success")

    return redirect(url_for("gallery_admin.list_photos"))


# ── New AJAX endpoint: uploads ONE photo at a time ──
@gallery_admin_bp.route("/upload-single", methods=["POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def upload_single_photo():
    f = request.files.get("photo")
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    if not f or not f.filename:
        return jsonify({"success": False, "error": "No file provided"}), 400

    try:
        result = upload_image(f, folder="kotd/gallery")
        photo = GalleryPhoto(
            title=title,
            description=description,
            image_url=result["url"],
            public_id=result["public_id"],
            created_by=current_user.id,
        )
        db.session.add(photo)
        db.session.commit()
        return jsonify({
            "success": True,
            "photo_id": photo.id,
            "url": result["url"],
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@gallery_admin_bp.route("/<int:photo_id>/edit", methods=["POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def edit_photo(photo_id):
    photo = GalleryPhoto.query.get_or_404(photo_id)
    photo.title = request.form.get("title", "").strip()
    photo.description = request.form.get("description", "").strip()
    photo.is_published = request.form.get("is_published") == "on"
    db.session.commit()
    flash("Photo updated.", "success")
    return redirect(url_for("gallery_admin.list_photos"))


@gallery_admin_bp.route("/<int:photo_id>/delete", methods=["POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def delete_photo(photo_id):
    photo = GalleryPhoto.query.get_or_404(photo_id)
    if photo.public_id:
        try:
            delete_image(photo.public_id)
        except Exception:
            pass
    db.session.delete(photo)
    db.session.commit()
    flash("Photo deleted.", "info")
    return redirect(url_for("gallery_admin.list_photos"))