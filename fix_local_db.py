"""
LOCAL DEV ONLY — nukes the local SQLite DB and rebuilds it directly from models.
Bypasses Alembic entirely. No migration history. Just tables.

DANGER: deletes instance/kotd.db and all data.
Do NOT run on Railway or any environment with real data.

Usage:
    python fix_local_db.py
"""
import os
import sys
import glob

# ── Safety guard ────────────────────────────────────────────────
if os.getenv("FLASK_ENV") == "production":
    print("[fix] Refusing to run with FLASK_ENV=production.")
    sys.exit(1)

DB_PATH = os.path.join("instance", "kotd.db")


def main():
    # 1. Delete the DB file and any WAL/journal sidecar files
    print("[fix] Deleting local database...")
    for path in glob.glob(DB_PATH + "*"):
        print(f"  removing {path}")
        os.remove(path)

    # Ensure instance/ exists
    os.makedirs("instance", exist_ok=True)

    # 2. Create all tables from models — no Alembic
    from app import create_app
    from app.extensions import db
    from app.models.user import User
    from app.models.member import Member
    from app.models.ministry import Ministry
    from app.models.family import Family
    from app.utils.roles import Role

    app = create_app()
    with app.app_context():
        print("[fix] Creating tables from models...")
        db.create_all()
        print("[fix] Tables created.")

        # 3. Seed families
        print("[fix] Seeding families...")
        FAMILIES = [
            "Opoku Onyinah Family",
            "James Mckweon Family",
            "M.K Yeboah Family",
            "Apostle Micheal Ntumi Family",
            "F.S Sarfo Family",
        ]
        for name in FAMILIES:
            if not Family.query.filter_by(name=name).first():
                db.session.add(Family(name=name))

        # 4. Seed ministries
        print("[fix] Seeding ministries...")
        MINISTRIES = [
            ("Women", "Women"),
            ("Men", "Men"),
            ("Youth", "Youth"),
            ("Children", "Children"),
            ("Evangelism", "Evangelism"),
            ("HUM", "HUM"),
            ("MPWDs", "MPWDs"),
            ("Chaplaincy", "Chaplaincy"),
            ("Chieftaincy", "Chieftaincy"),
            ("SOM", "SOM"),
            ("Counselling", "Counselling"),
        ]
        for name, category in MINISTRIES:
            if not Ministry.query.filter_by(name=name).first():
                db.session.add(Ministry(name=name, category=category))

        db.session.commit()
        print(f"  Families in DB: {Family.query.count()}")
        print(f"  Ministries in DB: {Ministry.query.count()}")

        # 5. Create Super Admin
        print("\n[fix] Creating Super Admin...")
        if User.query.filter_by(role=Role.SUPER_ADMIN).first():
            print("  Super Admin already exists, skipping.")
        else:
            email = input("  Email: ").strip()
            password = input("  Password: ").strip()
            first_name = input("  First name: ").strip() or "Super"
            last_name = input("  Last name: ").strip() or "Admin"

            u = User(
                email=email.lower(),
                first_name=first_name,
                last_name=last_name,
                role=Role.SUPER_ADMIN,
                is_active=True,
            )
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
            print(f"  Created: {u.email}")

    print("\n[fix] Done. Run: python run.py")


if __name__ == "__main__":
    main()