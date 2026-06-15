@echo off
setlocal EnableExtensions

echo APEX Platform preflight: checking stale gateway containers...
for /f "tokens=*" %%I in ('docker ps -a --filter "name=web-gateway" --format "{{.ID}}" 2^>nul') do (
    echo Removing stale gateway container %%I
    docker rm -f %%I
    if errorlevel 1 (
        echo ERROR: failed to remove stale gateway container %%I
        exit /b 1
    )
)

echo Starting APEX Platform with unified web gateway...
docker compose -f docker-compose.prod.yml up -d --build --remove-orphans
if errorlevel 1 (
    echo ERROR: APEX Platform failed to start. Review the Docker Compose output above.
    exit /b %errorlevel%
)

echo.
echo APEX Platform started successfully.
echo Main web:      http://localhost
echo CISO Dashboard: http://localhost/ciso-dashboard
echo Streamlit raw:  http://localhost/stream-backend/
echo API health:     http://localhost/api/health
echo.
