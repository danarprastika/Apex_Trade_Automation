FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir --force-reinstall pydantic \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY backend/app /app/app
COPY backend/alembic.ini /app/alembic.ini
COPY scripts/db_init.sh /app/scripts/db_init.sh
RUN chmod +x /app/scripts/db_init.sh

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=6 \
    CMD curl -sf http://localhost:8000/health || exit 1

CMD ["/bin/sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"]