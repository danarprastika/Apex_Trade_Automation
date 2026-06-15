#!/bin/sh
set -e
echo "Running database migrations..."
cd /app
alembic upgrade head
echo "Database migrations complete."