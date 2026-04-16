#!/bin/bash

# Airflow 3.x Quick Setup Script

set -e

# Ensure script runs from its containing directory (airflow/)
cd "$(dirname "$0")"

echo "=========================================="
echo "Airflow 3.x Docker Compose Setup"
echo "=========================================="
echo ""

# Set AIRFLOW_UID for Linux/Mac
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" ]]; then
    export AIRFLOW_UID=$(id -u 0)
    export AIRFLOW_GID=$(id -g 0)
    echo "✓ Set AIRFLOW_UID=$AIRFLOW_UID and AIRFLOW_GID=$AIRFLOW_GID"
fi

echo ""
echo "Starting Airflow 3.x services..."
echo ""

# Create required directories
mkdir -p dags logs plugins

# Fix permissions on host-mounted files/dirs so Airflow container can write logs
# Use a short-lived container to avoid requiring sudo on the host
if command -v docker >/dev/null 2>&1; then
    echo "Fixing ownership for host-mounted `logs` and password file (UID 50000)..."
    # Ensure files exist before attempting to chown
    touch simple_auth_manager_passwords.json || true
    mkdir -p logs
    docker run --rm -v "$(pwd)/logs":/target:rw alpine:3.18 sh -c "chown -R 50000:0 /target || true; chmod -R g+rwX /target || true"
    docker run --rm -v "$(pwd)/simple_auth_manager_passwords.json":/target/file:rw alpine:3.18 sh -c "chown 50000:0 /target/file || true; chmod 640 /target/file || true"
fi

# Start services
docker compose up -d

echo ""
echo "✓ Services started successfully!"
echo ""
echo "Waiting for Airflow to initialize..."
sleep 15

# Show status
echo ""
echo "=========================================="
echo "Airflow 3.x - Status Check"
echo "=========================================="
docker compose ps

echo ""
echo "=========================================="
echo "Quick Links:"
echo "=========================================="
echo ""
echo "🌐 Airflow Web UI: http://localhost:1013"
echo "   Username: airflow"
echo "   Password: airflow"
echo ""
echo "📊 PostgreSQL: localhost:5432"
echo "   Username: airflow"
echo "   Password: airflow"
echo ""
echo "🔴 Redis: localhost:6379"
echo ""
echo "=========================================="
echo "Useful Commands:"
echo "=========================================="
echo ""
echo "View logs:        docker compose logs -f airflow-webserver"
echo "List DAGs:        docker compose exec airflow-webserver airflow dags list"
echo "Stop services:    docker compose down"
echo "Stop and remove:  docker compose down -v"
echo "Restart services: docker compose restart"
echo ""
