from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.auth.decorators import role_required
from app.utils.roles import Role
from app.models.ministry import Ministry
from app.ministries.forms import MinistryForm


ministries_bp = Blueprint("ministries", __name__, url_prefix="/ministries")


@ministries_bp.route("/")
@login_required
@role_required(Role.SUPER_ADMIN, Role.ADMIN)
def list_ministries():
    ministries = Ministry.query.order_by(Ministry.name).all()
    return render_template("ministries/list.html", ministries=ministries)


@ministries_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required(Role.SUPER_ADMIN, Role.ADMIN)
def create_ministry():
    form = MinistryForm()
    if form.validate_on_submit():
        if Ministry.query.filter_by(name=form.name.data.strip()).first():
            flash("A ministry with that name already exists.", "danger")
            return render_template("ministries/form.html", form=form, ministry=None)

        m = Ministry(
            name=form.name.data.strip(),
            category=form.category.data,
            description=form.description.data,
            meeting_day=form.meeting_day.data,
            is_active=form.is_active.data,
        )
        db.session.add(m)
        db.session.commit()
        flash(f"Ministry {m.name} created.", "success")
        return redirect(url_for("ministries.list_ministries"))
    return render_template("ministries/form.html", form=form, ministry=None)


@ministries_bp.route("/<int:ministry_id>/edit", methods=["GET", "POST"])
@login_required
@role_required(Role.SUPER_ADMIN, Role.ADMIN)
def edit_ministry(ministry_id):
    m = Ministry.query.get_or_404(ministry_id)
    form = MinistryForm(obj=m)
    if form.validate_on_submit():
        existing = Ministry.query.filter(
            Ministry.name == form.name.data.strip(),
            Ministry.id != m.id,
        ).first()
        if existing:
            flash("Another ministry already uses that name.", "danger")
            return render_template("ministries/form.html", form=form, ministry=m)

        m.name = form.name.data.strip()
        m.category = form.category.data
        m.description = form.description.data
        m.meeting_day = form.meeting_day.data
        m.is_active = form.is_active.data
        db.session.commit()
        flash("Ministry updated.", "success")
        return redirect(url_for("ministries.list_ministries"))
    return render_template("ministries/form.html", form=form, ministry=m)


@ministries_bp.route("/<int:ministry_id>/delete", methods=["POST"])
@login_required
@role_required(Role.SUPER_ADMIN)
def delete_ministry(ministry_id):
    m = Ministry.query.get_or_404(ministry_id)
    if m.leaders.count() > 0:
        flash(
            f"Cannot delete {m.name} — {m.leaders.count()} leader(s) still assigned.",
            "danger",
        )
        return redirect(url_for("ministries.list_ministries"))
    db.session.delete(m)
    db.session.commit()
    flash(f"Ministry {m.name} deleted.", "info")
    return redirect(url_for("ministries.list_ministries"))