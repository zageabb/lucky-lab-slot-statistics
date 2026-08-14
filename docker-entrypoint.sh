#!/bin/sh
set -eu

mkdir -p /data
flask --app app:create_app db upgrade
flask --app app:create_app main seed
exec gunicorn --bind 0.0.0.0:5020 --workers 2 --threads 4 --timeout 120 'app:create_app()'
