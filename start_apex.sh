#!/bin/bash
set -euo pipefail

COMPOSE_FILE="docker-compose.prod.yml"

echo "=========================================="
echo "🛡️  APEX PLATFORM - STARTUP SEQUENCE"
echo "=========================================="

# Cleanup stale containers
echo "1. Cleaning stale containers..."
stale_gateways=$(docker ps -a --filter "name=web-gateway" --format "{{.ID}}" 2>/dev/null || true)
if [ -n "$stale_gateways" ]; then
    echo "$stale_gateways" | while read -r container_id; do
        echo "Removing stale gateway container $container_id"
        docker rm -f "$container_id" 2>/dev/null || true
    done
fi

# Build and start
echo "2. Building and starting services..."
docker compose -f "$COMPOSE_FILE" up -d --build --remove-orphans

# Wait for services to be healthy
echo "3. Waiting for services to be healthy..."
echo "   Checking postgres..."
until [ "$(docker compose -f "$COMPOSE_FILE" ps -q postgres | head -1 | xargs docker inspect -f '{{.State.Health.Status}}' 2>/dev/null || echo 'starting')" = "healthy" ]; do
    sleep 2
done

echo "   Checking redis..."
until [ "$(docker compose -f "$COMPOSE_FILE" ps -q redis | head -1 | xargs docker inspect -f '{{.State.Health.Status}}' 2>/dev/null || echo 'starting')" = "healthy" ]; do
    sleep 2
done

echo "   Checking backend..."
until [ "$(docker compose -f "$COMPOSE_FILE" ps -q backend | head -1 | xargs docker inspect -f '{{.State.Health.Status}}' 2>/dev/null || echo 'starting')" = "healthy" ]; do
    sleep 2
done

echo "   Checking frontend..."
until [ "$(docker compose -f "$COMPOSE_FILE" ps -q frontend | head -1 | xargs docker inspect -f '{{.State.Health.Status}}' 2>/dev/null || echo 'starting')" = "healthy" ]; do
    sleep 2
done

echo "   Checking ciso-dashboard..."
until [ "$(docker compose -f "$COMPOSE_FILE" ps -q ciso-dashboard | head -1 | xargs docker inspect -f '{{.State.Health.Status}}' 2>/dev/null || echo 'starting')" = "healthy" ]; do
    sleep 2
done

echo ""
echo "=========================================="
echo "✅ SEMUA SERVICE SUDAH SIAP!"
echo "=========================================="
echo ""
echo "🌐 ACCESS POINTS (http://localhost):"
echo "   /                 → Main Web UI (login)"
echo "   /dashboard        → React Dashboard"
echo "   /ciso-dashboard   → CISO Center (Streamlit)"
echo "   /health           → Health check (JSON)"
echo "   /api/             → API endpoints"
echo ""
echo "📊 SERVICE STATUS:"
docker compose -f "$COMPOSE_FILE" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo "=========================================="