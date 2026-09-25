from flask import Blueprint, render_template
from flask_login import login_required
from app.auth.decorators import role_required
from app.utils.roles import Role

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/super-admin")
@login_required
@role_required(Role.SUPER_ADMIN)
def super_admin():
    from app.models.member import Member
    from app.models.user import User
    from app.models.ministry import Ministry

    stats = {
        "total_members": Member.query.count(),
        "active_members": Member.query.filter_by(membership_status="active").count(),
        "total_staff": User.query.filter_by(is_active=True).count(),
        "total_ministries": Ministry.query.filter_by(is_active=True).count(),
    }
    recent = Member.query.order_by(Member.created_at.desc()).limit(5).all()
    return render_template("dashboard/super_admin.html", stats=stats, recent=recent)


@dashboard_bp.route("/admin")
@login_required
@role_required(Role.ADMIN, Role.SUPER_ADMIN)
def admin():
    return render_template("dashboard/admin.html")


@dashboard_bp.route("/financial-officer")
@login_required
@role_required(Role.FINANCIAL_OFFICER, Role.SUPER_ADMIN)
def financial_officer():
    return render_template("dashboard/financial_officer.html")


@dashboard_bp.route("/records-officer")
@login_required
@role_required(Role.RECORDS_OFFICER, Role.SUPER_ADMIN)
def records_officer():
    return render_template("dashboard/records_officer.html")


@dashboard_bp.route("/compliance-officer")
@login_required
@role_required(Role.COMPLIANCE_OFFICER, Role.SUPER_ADMIN)
def compliance_officer():
    return render_template("dashboard/compliance_officer.html")


@dashboard_bp.route("/data-officer")
@login_required
@role_required(Role.DATA_OFFICER, Role.SUPER_ADMIN)
def data_officer():
    return render_template("dashboard/data_officer.html")


@dashboard_bp.route("/communications-officer")
@login_required
@role_required(Role.COMMUNICATIONS_OFFICER, Role.SUPER_ADMIN)
def communications_officer():
    return render_template("dashboard/communications_officer.html")


@dashboard_bp.route("/programs-officer")
@login_required
@role_required(Role.PROGRAMS_OFFICER, Role.SUPER_ADMIN)
def programs_officer():
    return render_template("dashboard/programs_officer.html")


@dashboard_bp.route("/ministry-leader")
@login_required
@role_required(Role.MINISTRY_LEADER, Role.SUPER_ADMIN)
def ministry_leader():
    return render_template("dashboard/ministry_leader.html")