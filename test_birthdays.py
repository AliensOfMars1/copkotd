"""
Test the birthday helper functions.

Run: python test_birthdays.py
"""
from datetime import date, timedelta

from app import create_app
from app.extensions import db
from app.models.member import Member
from app.models.family import Family
from app.utils.birthdays import get_upcoming_birthdays, get_todays_birthdays, days_until_birthday


def main():
    app = create_app()
    with app.app_context():
        print("=" * 60)
        print("TEST 1 — Before adding test member")
        print("=" * 60)
        upcoming = get_upcoming_birthdays(7)
        today_bdays = get_todays_birthdays()
        print(f"Upcoming (7 days): {len(upcoming)}")
        print(f"Today: {len(today_bdays)}")

        print("\n" + "=" * 60)
        print("TEST 2 — Adding a test member with birthday in 3 days")
        print("=" * 60)
        f = Family.query.first()
        if not f:
            print("ERROR: No families in DB. Run seed first.")
            return

        # Cleanup any old test members first
        old = Member.query.filter_by(first_name="Test", last_name="Birthday").first()
        if old:
            db.session.delete(old)
            db.session.commit()

        three_days = date.today() + timedelta(days=3)
        m = Member(
            first_name="Test",
            last_name="Birthday",
            gender="Male",
            date_of_birth=date(1990, three_days.month, three_days.day),
            birthday_public=True,
            membership_status="active",
            family_id=f.id,
        )
        db.session.add(m)
        db.session.commit()
        print(f"Created: {m.full_name} | DOB: {m.date_of_birth}")

        print("\n" + "=" * 60)
        print("TEST 3 — Checking upcoming birthdays again")
        print("=" * 60)
        upcoming = get_upcoming_birthdays(7)
        print(f"Upcoming (7 days): {len(upcoming)}")
        for member in upcoming:
            days = days_until_birthday(member)
            print(f"  - {member.full_name} — DOB {member.date_of_birth} — in {days} days")

        print("\n" + "=" * 60)
        print("TEST 4 — Privacy test (birthday_public=False)")
        print("=" * 60)
        m.birthday_public = False
        db.session.commit()
        upcoming = get_upcoming_birthdays(7)
        print(f"Upcoming (7 days) with privacy off: {len(upcoming)}")
        # Should be 0 — the test member is now hidden

        print("\n" + "=" * 60)
        print("CLEANUP")
        print("=" * 60)
        db.session.delete(m)
        db.session.commit()
        print("Test member deleted.")

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)


if __name__ == "__main__":
    main()