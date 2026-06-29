#!/bin/bash
set -e

echo "==> Waiting for database..."
python -c "
import os, socket, time
url = os.environ.get('DATABASE_URL', '')
if url:
    host = url.split('@')[1].split(':')[0]
    port = url.split(':')[-1].split('/')[0]
    for i in range(30):
        try:
            s = socket.create_connection((host, int(port)), 2)
            s.close()
            break
        except Exception:
            if i == 29: exit(1)
            time.sleep(1)
"

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Seeding content..."
python manage.py seed_content

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "==> Starting server..."
exec gunicorn finance.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --threads 2 \
  --worker-class gthread \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
