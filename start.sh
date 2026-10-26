#!/bin/bash
set -e

echo "[start.sh] Running migrations..."
flask db upgrade

echo "[start.sh] Seeding Super Admin if needed..."
python seed_admin.py

echo "[start.sh] Seeding families and ministries..."
python seed_reference_data.py

echo "[start.sh] Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:$PORT run:app