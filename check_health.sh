#!/bin/bash
echo "=== APEX System Health Check ==="
docker compose -f docker-compose.prod.yml ps
echo ""
echo "Checking container status..."
docker compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.State}}"
echo ""
if [ "$(docker compose -f docker-compose.prod.yml ps -q 2>/dev/null | wc -l)" -gt 0 ]; then
    if [ "$(docker compose -f docker-compose.prod.yml ps --filter "status=running" -q 2>/dev/null | wc -l)" -eq "$(docker compose -f docker-compose.prod.yml ps -q 2>/dev/null | wc -l)" ]; then
        echo "All containers are UP and running."
    else
        echo "Some containers are not running. Check the status above."
    fi
else
    echo "No containers found. Run './start_apex.sh' to start the system."
fi