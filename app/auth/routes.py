from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.auth.forms import LoginForm
from app.utils.roles import Role

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


DASHBOARD_ROUTES = {
    Role.SUPER_ADMIN: "dashboard.super_admin",
    Role.ADMIN: "dashboard.admin",
    Role.FINANCIAL_OFFICER: "dashboard.financial_officer",
    Role.RECORDS_OFFICER: "dashboard.records_officer",
    Role.COMPLIANCE_OFFICER: "dashboard.compliance_officer",
    Role.DATA_OFFICER: "dashboard.data_officer",
    Role.COMMUNICATIONS_OFFICER: "dashboard.communications_officer",
    Role.PROGRAMS_OFFICER: "dashboard.programs_officer",
    Role.MINISTRY_LEADER: "dashboard.ministry_leader",
}


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(DASHBOARD_ROUTES.get(current_user.role, "main.index")))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.is_active and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash(f"Welcome back, {user.first_name}.", "success")
            return redirect(url_for(DASHBOARD_ROUTES.get(user.role, "main.index")))
        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))