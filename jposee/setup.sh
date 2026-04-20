#!/bin/bash
# jPOS EE Setup and Startup Script

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JPOSEE_DIR="$PROJECT_ROOT/jposee"

echo "========================================"
echo "jPOS EE Setup & Startup Script"
echo "========================================"
echo ""

# Check if jPOS EE binaries are present
if [ -f "$JPOSEE_DIR/lib/jposee-"* ] 2>/dev/null; then
    echo "✓ jPOS EE binaries found"
else
    echo "⚠ jPOS EE binaries not found in lib/"
    echo "  To use full jPOS EE features, place JAR in: $JPOSEE_DIR/lib/"
    echo ""
fi

# Verify directory structure
echo "Verifying directory structure..."
mkdir -p "$JPOSEE_DIR/log" "$JPOSEE_DIR/deploy" "$JPOSEE_DIR/config"
echo "✓ Directories ready"
echo ""

# Build Docker image
echo "Building jPOS EE Docker image..."
cd "$PROJECT_ROOT"
docker compose build cms-jposee

echo ""
echo "========================================"
echo "Ready to start jPOS EE container"
echo "========================================"
echo ""
echo "To start: docker compose up cms-jposee -d"
echo "To view logs: docker logs -f cms-jposee"
echo "To stop: docker compose stop cms-jposee"
echo ""
