#!/bin/sh
# Web startup must not perform database migrations or seed data.
# See scripts/lucky-lab-db-maintenance.sh for separately approved operations.
set -eu

mkdir -p "${LUCKY_LAB_DATA_DIR:-/data}"
exec gunicorn --bind 0.0.0.0:5020 --workers 2 --threads 4 --timeout 120 'app:create_app()'
