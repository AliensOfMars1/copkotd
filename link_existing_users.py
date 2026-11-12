"""
One-off (idempotent) script to link existing User accounts that have no
member_id to newly-created Member records.

Safe to run repeatedly — skips users that are already linked.
Works both interactively (local dev) and non-interactively (Railway deploy).

Local:
    python link_existing_users.py

Railway:
    Called from start.sh → runs in non-interactive mode.
    Uses env vars LINK_FAMILY (optional, default = first family),
    and leaves gender/DOB blank unless LINK_GENDER / LINK_DOB set.
"""
import os
import sys
from datetime import datetime

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.member import Member
from app.models.family import Family


def pick_family(interactive: bool, label: str):
    families = Family.query.order_by(Family.name).all()
    if not families:
        print(f"[link] No families in DB. Create one first.")
        return None

    print(f"\nFamilies available for {label}:")
    for i, f in enumerate(families, 1):
        print(f"  {i}. {f.name}")

    if not interactive:
        env_choice = os.getenv("LINK_FAMILY")
        if env_choice:
            match = next((f for f in families if f.name.lower() == env_choice.lower()), None)
            if match:
                return match
        return families[0]

    while True:
        raw = input(f"Choose family [1-{len(families)}] (Enter = 1): ").strip()
        if not raw:
            return families[0]
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(families):
                return families[idx]
        except ValueError:
            pass
        print("  Invalid choice, try again.")


def prompt(interactive: bool, label: str, env_var: str = None, default: str = "") -> str:
    if not interactive:
        return os.getenv(env_var, default) if env_var else default
    raw = input(f"{label} (Enter = blank): ").strip()
    return raw or default


def parse_dob(raw: str):
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        print(f"  [warn] Invalid date format '{raw}', leaving DOB blank.")
        return None


def main():
    interactive = sys.stdin.isatty() and not os.getenv("LINK_NONINTERACTIVE")

    app = create_app()
    with app.app_context():
        unlinked = User.query.filter(User.member_id == None).order_by(User.id).all()

        if not unlinked:
            print("[link] No unlinked users. Nothing to do.")
            return

        print(f"[link] Found {len(unlinked)} unlinked user(s).")

        for u in unlinked:
            print(f"\n── {u.full_name} ({u.role}, {u.email}) ──")

            # Skip if a Member with the same name already exists — link to it
            existing = Member.query.filter(
                Member.first_name == u.first_name,
                Member.last_name == u.last_name,
            ).first()

            if existing:
                if existing.user_account:
                    print(f"  [skip] Member '{existing.full_name}' already has a user account. Manual fix needed.")
                    continue
                u.member_id = existing.id
                db.session.commit()
                print(f"  [link] Linked user to existing Member #{existing.id} ({existing.full_name}).")
                continue

            # Otherwise, create a new Member
            family = pick_family(interactive, u.full_name)
            if not family:
                print("  [skip] No family available, can't create Member.")
                continue

            gender_raw = prompt(interactive, "Gender (Male/Female)", env_var="LINK_GENDER")
            gender = gender_raw if gender_raw in ("Male", "Female") else None

            dob_raw = prompt(interactive, "Date of birth (YYYY-MM-DD)", env_var="LINK_DOB")
            dob = parse_dob(dob_raw)

            member = Member(
                first_name=u.first_name,
                last_name=u.last_name,
                phone=u.phone,
                gender=gender,
                date_of_birth=dob,
                family_id=family.id,
                membership_status="active",
                created_by=u.id,
                updated_by=u.id,
            )
            db.session.add(member)
            db.session.flush()

            u.member_id = member.id
            db.session.commit()

            print(f"  [created] Member #{member.id} ({member.full_name}) in {family.name}.")
            print(f"  [linked] User → Member #{member.id}.")

        print("\n[link] Done.")


if __name__ == "__main__":
    main()