#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python manage.py migrate
python manage.py collectstatic --noinput
gunicorn InternBuddy.asgi:application -w 4 -k InternBuddy.asgi.UvicornWorker --bind 0.0.0.0:80
