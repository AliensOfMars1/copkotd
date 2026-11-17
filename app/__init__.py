from flask import Flask, request
from config import Config
from app.extensions import db, login_manager, bcrypt, migrate, mail, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Init Cloudinary
    from app.utils.cloudinary import init_cloudinary
    init_cloudinary(app)

    # Import models so Alembic sees them
    from app import models  # noqa

    # User loader
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Markdown filter ────────────────────────────────
    import markdown as md

    @app.template_filter("markdown")
    def markdown_filter(text):
        if not text:
            return ""
        return md.markdown(text, extensions=["fenced_code", "tables", "nl2br"])

    # ── Birthday context processor ─────────────────────
    # Injects birthday data into every dashboard template.
    # Only runs for /dashboard/* routes to avoid wasted queries
    # on public pages.
    @app.context_processor
    def inject_birthdays():
        from flask_login import current_user
        if not current_user.is_authenticated:
            return {}
        # Only query on dashboard pages
        if not request.path.startswith("/dashboard/"):
            return {}

        from app.utils.birthdays import (
            get_todays_birthdays,
            get_upcoming_birthdays,
            days_until_birthday,
        )
        return {
            "todays_birthdays": get_todays_birthdays(),
            "upcoming_birthdays": get_upcoming_birthdays(days_ahead=7),
            "days_until": days_until_birthday,
        }

    # Register blueprints
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.members.routes import members_bp
    from app.users.routes import users_bp
    from app.ministries.routes import ministries_bp
    from app.families.routes import families_bp
    from app.content.routes import content_bp
    from app.content.gallery_routes import gallery_admin_bp
    from app.main.gallery import gallery_bp
    from app.main.sitemap import sitemap_bp
    from app.main.announcements import announcements_bp
    from app.content.health_admin import health_admin_bp
    from app.main.health import health_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(ministries_bp)
    app.register_blueprint(families_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(gallery_admin_bp)
    app.register_blueprint(gallery_bp)
    app.register_blueprint(sitemap_bp)
    app.register_blueprint(announcements_bp)
    app.register_blueprint(health_admin_bp)
    app.register_blueprint(health_bp)

    return app