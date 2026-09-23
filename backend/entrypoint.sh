#!/bin/sh
set -eu

echo "[entrypoint] waiting for PostgreSQL..."
python <<'PY'
import os, sys, time
import psycopg2
host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))
deadline = time.time() + 60
while True:
    try:
        conn = psycopg2.connect(
            host=host, port=port,
            dbname=os.environ.get("POSTGRES_DB", "codetools"),
            user=os.environ.get("POSTGRES_USER", "codetools"),
            password=os.environ.get("POSTGRES_PASSWORD", ""),
            connect_timeout=3,
        )
        conn.close()
        print("[entrypoint] PostgreSQL is ready.")
        break
    except Exception as exc:
        if time.time() >= deadline:
            print(exc, file=sys.stderr)
            sys.exit(1)
        time.sleep(1)
PY

mkdir -p /app/staticfiles
python manage.py migrate --noinput
python manage.py seed_site
python manage.py collectstatic --noinput
python manage.py ensure_superuser
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
