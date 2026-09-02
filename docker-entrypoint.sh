#!/bin/sh
set -e

# Wait for the database to accept connections (dev DATABASES uses DB_HOST/DB_NAME).
if [ -n "$DB_HOST" ]; then
  echo "Waiting for postgres at $DB_HOST..."
  until python - <<'PYEOF'
import os, socket, sys
host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", 5432))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
try:
    s.connect((host, port))
    sys.exit(0)
except OSError:
    sys.exit(1)
PYEOF
  do
    sleep 1
  done
  echo "Postgres is up."
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
