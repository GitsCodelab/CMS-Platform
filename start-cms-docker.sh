#!/bin/bash
# CMS Platform Quick Start Script

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║         CMS Platform - Quick Start                       ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

PROJECT_DIR="/home/samehabib/CMS-Platform"

# Check if docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

# Start Docker Compose Services
echo "📦 Starting Docker services (Oracle, PostgreSQL, Airflow, Backend, Frontend, APIM)..."
cd "$PROJECT_DIR"
docker compose up -d

# Wait for services to start
sleep 5

echo ""
echo "✅ Docker services started"
echo ""

# Display service status
echo "📊 Service Status:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep cms | sed 's/^/   /'

echo ""
echo "💡 Tips:"
echo "   • Access frontend at http://localhost:3000"
echo "   • Access backend health at http://localhost:8000/health"
echo "   • Stop services: docker compose down"
echo ""
