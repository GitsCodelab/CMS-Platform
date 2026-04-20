#!/bin/bash
# WSO2 API Manager Database Initialization Script
# Initializes PostgreSQL database with all required tables for WSO2 APIM

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INIT_SCRIPT="$SCRIPT_DIR/init_wso2_apim_db.py"

if [ ! -f "$INIT_SCRIPT" ]; then
    echo "❌ Error: init_wso2_apim_db.py not found in $SCRIPT_DIR"
    exit 1
fi

echo "🔄 Initializing WSO2 API Manager database..."
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
    docker exec cms-backend python3 /tmp/init_wso2_apim_db.py localhost
else
    docker exec cms-backend python3 /tmp/init_wso2_apim_db.py
fi

echo ""
echo "✅ WSO2 APIM database initialization complete!"
echo ""
echo "📊 Database Details:"
echo "   Host: cms-postgresql"
echo "   Port: 5432"
echo "   Database: wso2am"
echo "   Tables: 11 core tables + indexes"
echo "   Default Tiers: Bronze, Silver, Gold, Platinum, Unlimited"
echo "   Alert Types: 7 predefined alerts"
echo ""
echo "🚀 Next steps:"
echo "   1. Start WSO2 APIM: docker compose up -d cms-apim"
echo "   2. Access UI: https://localhost:9443/carbon"
echo "   3. Developer Portal: https://localhost:9443/devportal"
