from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, abort
)
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.extensions import db
from app.auth.decorators import role_required
from app.utils.roles import Role
from app.models.member import Member
from app.members.forms import MemberForm
from werkzeug.utils import secure_filename
from app.utils.cloudinary import upload_image, delete_image

members_bp = Blueprint("members", __name__, url_prefix="/members")


ALLOWED_ROLES = (Role.SUPER_ADMIN, Role.ADMIN, Role.RECORDS_OFFICER)


@members_bp.route("/")
@login_required
@role_required(*ALLOWED_ROLES)
def list_members():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)

    query = Member.query

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Member.first_name.ilike(like),
                Member.last_name.ilike(like),
                Member.phone.ilike(like),
                Member.email.ilike(like),
            )
        )

    if status:
        query = query.filter(Member.membership_status == status)

    pagination = query.order_by(Member.last_name, Member.first_name).paginate(
        page=page, per_page=25, error_out=False
    )

    return render_template(
        "members/list.html",
        pagination=pagination,
        members=pagination.items,
        q=q,
        status=status,
    )


@members_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def create_member():
    form = MemberForm()
    if form.validate_on_submit():
        member = Member()
        # Populate all fields EXCEPT 'photo' (that's a file, not a column)
        photo_file = form.photo.data
        form.photo.data = None  # prevent populate_obj from trying to assign it
        form.populate_obj(member)

        # Upload photo if provided
        if photo_file and photo_file.filename:
            try:
                result = upload_image(photo_file, folder="kotd/members")
                member.photo_url = result["url"]
            except Exception as e:
                flash(f"Photo upload failed: {e}", "warning")
                # Continue without photo — don't block the save

        member.created_by = current_user.id
        member.updated_by = current_user.id
        db.session.add(member)
        db.session.commit()
        flash(f"Member {member.full_name} added.", "success")
        return redirect(url_for("members.view_member", member_id=member.id))
    return render_template("members/form.html", form=form, member=None)


@members_bp.route("/<int:member_id>")
@login_required
@role_required(*ALLOWED_ROLES)
def view_member(member_id):
    member = Member.query.get_or_404(member_id)
    return render_template("members/detail.html", member=member)


@members_bp.route("/<int:member_id>/edit", methods=["GET", "POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def edit_member(member_id):
    member = Member.query.get_or_404(member_id)
    form = MemberForm(obj=member)

    if form.validate_on_submit():
        photo_file = form.photo.data
        form.photo.data = None
        form.populate_obj(member)

        # If a new photo was uploaded, replace the old one
        if photo_file and photo_file.filename:
            try:
                # Delete old photo from Cloudinary if it exists
                if member.photo_url:
                    # Extract public_id from URL
                    # URL format: https://res.cloudinary.com/{cloud}/image/upload/v{ver}/{public_id}.{ext}
                    try:
                        old_public_id = member.photo_url.split("/upload/")[1].split("/", 1)[1].rsplit(".", 1)[0]
                        delete_image(old_public_id)
                    except Exception as e:
                        print(f"[cleanup] Failed to delete old photo: {e}")
                    # Continue regardless — deletion is best-effort

                result = upload_image(photo_file, folder="kotd/members")
                member.photo_url = result["url"]
            except Exception as e:
                flash(f"Photo upload failed: {e}", "warning")

        member.updated_by = current_user.id
        db.session.commit()
        flash("Member updated.", "success")
        return redirect(url_for("members.view_member", member_id=member.id))

    return render_template("members/form.html", form=form, member=member)


@members_bp.route("/<int:member_id>/delete", methods=["POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    name = member.full_name

    # Delete photo from Cloudinary (best-effort)
    if member.photo_url:
        try:
            public_id = member.photo_url.split("/upload/")[1].split("/", 1)[1].rsplit(".", 1)[0]
            delete_image(public_id)
        except Exception as e:
            print(f"[cleanup] Failed to delete photo: {e}")

    db.session.delete(member)
    db.session.commit()
    flash(f"Member {name} deleted.", "info")
    return redirect(url_for("members.list_members"))