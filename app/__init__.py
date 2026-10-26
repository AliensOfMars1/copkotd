from flask import Flask
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

    # Import models so Alembic sees them
    from app import models  # noqa

    # User loader
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.members.routes import members_bp
    from app.users.routes import users_bp
    from app.ministries.routes import ministries_bp
    from app.families.routes import families_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(ministries_bp)
    app.register_blueprint(families_bp)

    return app