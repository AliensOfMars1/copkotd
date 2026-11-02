"""
Runs on every deploy. Safe to run repeatedly.
Creates the Super Admin if the users table is empty.
"""
import os
import sys

from app import create_app
from app.extensions import db
from app.models.user import User
from app.utils.roles import Role


def main():
    app = create_app()
    with app.app_context():
        # Skip if a Super Admin already exists
        existing = User.query.filter_by(role=Role.SUPER_ADMIN).first()
        if existing:
            print(f"[seed_admin] Super Admin already exists: {existing.email}")
            return

        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")
        first_name = os.getenv("ADMIN_FIRST_NAME", "Super")
        last_name = os.getenv("ADMIN_LAST_NAME", "Admin")

        if not email or not password:
            print("[seed_admin] ADMIN_EMAIL or ADMIN_PASSWORD missing. Skipping.")
            sys.exit(0)

        u = User(
            email=email.lower().strip(),
            first_name=first_name,
            last_name=last_name,
            role=Role.SUPER_ADMIN,
            is_active=True,
        )
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        print(f"[seed_admin] Super Admin created: {u.email}")


if __name__ == "__main__":
    main()