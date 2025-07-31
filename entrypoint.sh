#!/bin/sh

DB_PATH="/app/sla_agent.db"
if [ -f "$DB_PATH" ]; then
    echo "Removing old database at $DB_PATH"
    rm "$DB_PATH"
fi

echo "Starting app with Gunicorn..."
exec gunicorn -b 0.0.0.0:5000 wsgi:app
