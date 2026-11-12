from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.auth.decorators import role_required
from app.utils.roles import Role
from app.models.user import User
from app.users.forms import UserCreateForm, UserEditForm
import secrets
import string


users_bp = Blueprint("users", __name__, url_prefix="/users")


def _generate_temp_password(length=10):
    """Generate a temp password: at least one digit, mixed case."""
    alphabet = string.ascii_letters + string.digits
    while True:
        pwd = "".join(secrets.choice(alphabet) for _ in range(length))
        if any(c.isdigit() for c in pwd) and any(c.isalpha() for c in pwd):
            return pwd


@users_bp.route("/")
@login_required
@role_required(Role.SUPER_ADMIN)
def list_users():
    show = request.args.get("show", "active")
    query = User.query
    if show == "active":
        query = query.filter_by(is_active=True)
    elif show == "inactive":
        query = query.filter_by(is_active=False)

    users = query.order_by(User.last_name, User.first_name).all()
    return render_template("users/list.html", users=users, show=show)


@users_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required(Role.SUPER_ADMIN)
def create_user():
    from app.models.member import Member

    form = UserCreateForm()
    if form.validate_on_submit():
        # 1. Email uniqueness
        if User.query.filter_by(email=form.email.data.lower().strip()).first():
            flash("A user with that email already exists.", "danger")
            return render_template("users/form.html", form=form, user=None)

        # 2. Ministry required for ministry leaders
        if form.role.data == Role.MINISTRY_LEADER and not form.ministry_id.data:
            flash("Ministry Leaders must be assigned to a ministry.", "danger")
            return render_template("users/form.html", form=form, user=None)

        # 3. Resolve / create the Member record
        member = None
        if form.member_mode.data == "existing":
            if not form.existing_member_id.data:
                flash("Please select an existing member.", "danger")
                return render_template("users/form.html", form=form, user=None)
            member = Member.query.get(form.existing_member_id.data)
            if not member:
                flash("Selected member not found.", "danger")
                return render_template("users/form.html", form=form, user=None)
            if member.user_account:
                flash(f"{member.full_name} already has a user account.", "danger")
                return render_template("users/form.html", form=form, user=None)
        else:  # create new member
            if not form.member_first_name.data or not form.member_last_name.data:
                flash("First and last name are required for a new member.", "danger")
                return render_template("users/form.html", form=form, user=None)
            if not form.member_family_id.data:
                flash("Family group is required for a new member.", "danger")
                return render_template("users/form.html", form=form, user=None)

            member = Member(
                first_name=form.member_first_name.data.strip(),
                last_name=form.member_last_name.data.strip(),
                gender=form.member_gender.data or None,
                date_of_birth=form.member_date_of_birth.data,
                phone=form.member_phone.data,
                family_id=form.member_family_id.data,
                membership_status="active",
                created_by=current_user.id,
                updated_by=current_user.id,
            )
            db.session.add(member)
            db.session.flush()  # get member.id without committing

        # 4. Create User linked to Member (name comes from Member)
        temp_pwd = _generate_temp_password()
        u = User(
            email=form.email.data.lower().strip(),
            first_name=member.first_name,
            last_name=member.last_name,
            phone=member.phone,
            role=form.role.data,
            ministry_id=form.ministry_id.data if form.role.data == Role.MINISTRY_LEADER else None,
            is_active=form.is_active.data,
            member_id=member.id,
            created_by=current_user.id,
        )
        u.set_password(temp_pwd)
        db.session.add(u)
        db.session.commit()

        flash(
            f"User {u.full_name} created and linked to member {member.full_name}. "
            f"Temporary password: {temp_pwd} — share it securely.",
            "success",
        )
        return redirect(url_for("users.list_users"))

    return render_template("users/form.html", form=form, user=None)


@users_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@role_required(Role.SUPER_ADMIN)
def edit_user(user_id):
    u = User.query.get_or_404(user_id)
    form = UserEditForm(obj=u)

    if form.validate_on_submit():
        if u.id == current_user.id and form.role.data != Role.SUPER_ADMIN:
            flash("You cannot change your own role away from Super Admin.", "danger")
            return render_template("users/form.html", form=form, user=u)

        if u.id == current_user.id and not form.is_active.data:
            flash("You cannot deactivate your own account.", "danger")
            return render_template("users/form.html", form=form, user=u)

        existing = User.query.filter(
            User.email == form.email.data.lower().strip(),
            User.id != u.id,
        ).first()
        if existing:
            flash("Another user already has that email.", "danger")
            return render_template("users/form.html", form=form, user=u)

        if form.role.data == Role.MINISTRY_LEADER and not form.ministry_id.data:
            flash("Ministry Leaders must be assigned to a ministry.", "danger")
            return render_template("users/form.html", form=form, user=u)

        u.email = form.email.data.lower().strip()
        u.phone = form.phone.data
        u.role = form.role.data
        u.ministry_id = form.ministry_id.data if form.role.data == Role.MINISTRY_LEADER else None
        u.is_active = form.is_active.data

        # If this user is linked to a member, keep the User's name in sync
        if u.member:
            u.first_name = u.member.first_name
            u.last_name = u.member.last_name

        db.session.commit()
        flash("User updated.", "success")
        return redirect(url_for("users.list_users"))

    return render_template("users/form.html", form=form, user=u)


@users_bp.route("/<int:user_id>/toggle", methods=["POST"])
@login_required
@role_required(Role.SUPER_ADMIN)
def toggle_user(user_id):
    u = User.query.get_or_404(user_id)
    if u.id == current_user.id:
        flash("You cannot deactivate your own account.", "danger")
        return redirect(url_for("users.list_users"))

    u.is_active = not u.is_active
    db.session.commit()
    flash(f"{u.full_name} is now {'active' if u.is_active else 'inactive'}.", "info")
    return redirect(url_for("users.list_users"))


@users_bp.route("/<int:user_id>/reset-password", methods=["POST"])
@login_required
@role_required(Role.SUPER_ADMIN)
def reset_password(user_id):
    u = User.query.get_or_404(user_id)
    temp_pwd = _generate_temp_password()
    u.set_password(temp_pwd)
    db.session.commit()
    flash(f"Password reset for {u.full_name}. New temporary password: {temp_pwd}", "success")
    return redirect(url_for("users.list_users"))