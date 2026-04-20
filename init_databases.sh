#!/bin/bash
# Convenient wrapper to initialize test tables for both databases
# Usage: ./init_databases.sh [localhost]

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INIT_SCRIPT="$SCRIPT_DIR/init_test_tables.py"

if [ ! -f "$INIT_SCRIPT" ]; then
    echo "❌ Error: init_test_tables.py not found in $SCRIPT_DIR"
    exit 1
fi

echo "🔄 Initializing test tables in Oracle and PostgreSQL..."
echo ""

# Check if backend container is running
if ! docker ps | grep -q cms-backend; then
    echo "❌ Error: cms-backend container is not running"
    echo "Please run: docker compose up -d"
    exit 1
fi

# Copy script to backend container and execute
docker cp "$INIT_SCRIPT" cms-backend:/tmp/ > /dev/null 2>&1

# Run the script with optional argument for localhost
if [ "$1" = "localhost" ]; then
    docker exec cms-backend python3 /tmp/init_test_tables.py localhost
else
    docker exec cms-backend python3 /tmp/init_test_tables.py
fi

echo ""
echo "✅ Test table initialization complete!"
echo ""
echo "📊 Verify data with:"
echo "   curl http://localhost:8000/oracle/test"
echo "   curl http://localhost:8000/postgres/test"
