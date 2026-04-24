#!/bin/bash
# CMS Platform with jPOS-EE Quick Start Script

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   CMS Platform + jPOS-EE Gateway - Quick Start           ║"
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
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   Next Step: Start jPOS-EE Gateway in another terminal   ║"
echo "╠═══════════════════════════════════════════════════════════╣"
echo "║  Run:  cd $PROJECT_DIR/jpos-ee                           ║"
echo "║        java -jar target/jpos-ee-1.0.0.jar               ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "💡 Tips:"
echo "   • After jPOS-EE starts, you can run: python3 test_jpos_iso.py"
echo "   • View gateway logs: tail -f /tmp/jpos-gateway.log"
echo "   • Stop services: docker compose down"
echo ""
