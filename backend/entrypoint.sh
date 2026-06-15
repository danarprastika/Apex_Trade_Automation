#!/bin/sh
set -e

echo "Running database migrations..."
retry_count=0
max_retries=10
while [ $retry_count -lt $max_retries ]; do
    if alembic -c /app/alembic.ini upgrade head; then
        echo "Migration successful"
        break
    else
        retry_count=$((retry_count + 1))
        echo "Migration attempt $retry_count failed, retrying in 5s..."
        sleep 5
    fi
done

if [ $retry_count -eq $max_retries ]; then
    echo "Migration failed after $max_retries attempts"
    exit 1
fi

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4