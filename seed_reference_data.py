"""
Idempotent seed of reference data: 5 families + 11 ministries.
Safe to run on every deploy.
"""
from app import create_app
from app.extensions import db
from app.models.family import Family
from app.models.ministry import Ministry


FAMILIES = [
    "Opoku Onyinah Family",
    "James Mckweon Family",
    "M.K Yeboah Family",
    "Apostle Micheal Ntumi Family",
    "F.S Sarfo Family",
]

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


def main():
    app = create_app()
    with app.app_context():
        families_added = 0
        for name in FAMILIES:
            if not Family.query.filter_by(name=name).first():
                db.session.add(Family(name=name))
                families_added += 1

        ministries_added = 0
        for name, category in MINISTRIES:
            if not Ministry.query.filter_by(name=name).first():
                db.session.add(Ministry(name=name, category=category))
                ministries_added += 1

        db.session.commit()
        print(f"[seed] Families added: {families_added}")
        print(f"[seed] Ministries added: {ministries_added}")


if __name__ == "__main__":
    main()