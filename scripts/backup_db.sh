#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="${BACKUP_DIR}/apex_db_${TIMESTAMP}.tar.gz"

mkdir -p "${BACKUP_DIR}"

docker compose -f "${COMPOSE_FILE}" exec -T postgres pg_dump -U "${POSTGRES_USER:-apex}" "${POSTGRES_DB:-apex_db}" | gzip > "${OUTPUT_FILE}"

echo "Backup saved to ${OUTPUT_FILE}"
