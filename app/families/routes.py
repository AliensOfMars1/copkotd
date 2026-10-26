from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.auth.decorators import role_required
from app.utils.roles import Role
from app.models.family import Family
from app.models.member import Member
from app.families.forms import FamilyForm


families_bp = Blueprint("families", __name__, url_prefix="/families")


ALLOWED_ROLES = (Role.SUPER_ADMIN, Role.ADMIN, Role.RECORDS_OFFICER)


@families_bp.route("/")
@login_required
@role_required(*ALLOWED_ROLES)
def list_families():
    families = Family.query.order_by(Family.name).all()
    return render_template("families/list.html", families=families)


@families_bp.route("/<int:family_id>")
@login_required
@role_required(*ALLOWED_ROLES)
def view_family(family_id):
    family = Family.query.get_or_404(family_id)
    members = family.members.order_by(Member.last_name, Member.first_name).all()
    return render_template("families/detail.html", family=family, members=members)


@families_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required(Role.SUPER_ADMIN, Role.ADMIN)
def create_family():
    form = FamilyForm()
    if form.validate_on_submit():
        if Family.query.filter_by(name=form.name.data.strip()).first():
            flash("A family with that name already exists.", "danger")
            return render_template("families/form.html", form=form, family=None)

        f = Family(
            name=form.name.data.strip(),
            description=form.description.data,
            leader_id=form.leader_id.data,
            is_active=form.is_active.data,
        )
        db.session.add(f)
        db.session.commit()
        flash(f"Family {f.name} created.", "success")
        return redirect(url_for("families.list_families"))
    return render_template("families/form.html", form=form, family=None)


@families_bp.route("/<int:family_id>/edit", methods=["GET", "POST"])
@login_required
@role_required(Role.SUPER_ADMIN, Role.ADMIN)
def edit_family(family_id):
    f = Family.query.get_or_404(family_id)
    form = FamilyForm(obj=f)
    if form.validate_on_submit():
        existing = Family.query.filter(
            Family.name == form.name.data.strip(),
            Family.id != f.id,
        ).first()
        if existing:
            flash("Another family already uses that name.", "danger")
            return render_template("families/form.html", form=form, family=f)

        f.name = form.name.data.strip()
        f.description = form.description.data
        f.leader_id = form.leader_id.data
        f.is_active = form.is_active.data
        db.session.commit()
        flash("Family updated.", "success")
        return redirect(url_for("families.list_families"))
    return render_template("families/form.html", form=form, family=f)


@families_bp.route("/<int:family_id>/delete", methods=["POST"])
@login_required
@role_required(Role.SUPER_ADMIN)
def delete_family(family_id):
    f = Family.query.get_or_404(family_id)
    if f.member_count > 0:
        flash(
            f"Cannot delete {f.name} — {f.member_count} member(s) still assigned.",
            "danger",
        )
        return redirect(url_for("families.list_families"))
    db.session.delete(f)
    db.session.commit()
    flash(f"Family {f.name} deleted.", "info")
    return redirect(url_for("families.list_families"))