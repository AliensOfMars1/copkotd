"""
Birthday-related helpers.

All functions return Member objects with upcoming or today's birthdays.
Handles year wrap-around (e.g., Dec 28 → Jan 4).
"""
from datetime import date, datetime, timedelta
from sqlalchemy import func

from app.extensions import db
from app.models.member import Member


def _today():
    return date.today()


def get_upcoming_birthdays(days_ahead=7):
    """
    Return members whose birthday is between today and `days_ahead` days from now.
    Handles year boundaries correctly.
    Includes members whose birthday is TODAY.
    Only returns members with birthday_public = True.
    """
    today = _today()
    today_md = today.strftime("%m-%d")

    end_date = today + timedelta(days=days_ahead)
    end_md = end_date.strftime("%m-%d")

    query = Member.query.filter(
        Member.date_of_birth.isnot(None),
        Member.membership_status == "active",
        Member.birthday_public == True,
    )

    # Handle year boundary: e.g., Dec 28 + 7 days = Jan 4
    if end_date.year == today.year:
        query = query.filter(
            func.strftime("%m-%d", Member.date_of_birth).between(today_md, end_md)
        )
    else:
        query = query.filter(
            (func.strftime("%m-%d", Member.date_of_birth) >= today_md) |
            (func.strftime("%m-%d", Member.date_of_birth) <= end_md)
        )

    return query.order_by(func.strftime("%m-%d", Member.date_of_birth)).all()


def get_todays_birthdays():
    """Return members whose birthday is exactly today. Only birthday_public = True."""
    today = _today()
    today_md = today.strftime("%m-%d")

    return Member.query.filter(
        Member.date_of_birth.isnot(None),
        Member.membership_status == "active",
        Member.birthday_public == True,
        func.strftime("%m-%d", Member.date_of_birth) == today_md,
    ).all()


def days_until_birthday(member):
    """Days until a member's next birthday (0 if today)."""
    if not member.date_of_birth:
        return None

    today = _today()
    dob = member.date_of_birth

    this_year = date(today.year, dob.month, dob.day)
    if this_year < today:
        next_year = date(today.year + 1, dob.month, dob.day)
        return (next_year - today).days
    return (this_year - today).days