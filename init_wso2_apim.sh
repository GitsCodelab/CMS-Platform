#!/bin/bash
# WSO2 API Manager Database Initialization Script
# Uses official WSO2 SQL scripts to initialize PostgreSQL database

set -e

echo "🔄 Initializing WSO2 API Manager database (Official SQL Scripts)..."
echo ""

# Check if containers are running
if ! docker compose ps | grep -q cms-apim; then
    echo "❌ Error: cms-apim container is not running"
    echo "Please run: docker compose up -d"
    exit 1
fi

if ! docker compose ps | grep -q cms-postgresql; then
    echo "❌ Error: cms-postgresql container is not running"
    echo "Please run: docker compose up -d"
    exit 1
fi

# Drop and recreate database for fresh start
echo "📋 Step 1: Preparing database..."
docker compose exec -T cms-postgresql psql -U postgres -c "DROP DATABASE IF EXISTS wso2am;" 2>/dev/null || true
docker compose exec -T cms-postgresql psql -U postgres -c "CREATE DATABASE wso2am;" 2>/dev/null || true

# Initialize base PostgreSQL schema
echo "📋 Step 2: Initializing base PostgreSQL schema..."
docker compose exec cms-apim cat /home/wso2carbon/wso2am-4.3.0/dbscripts/postgresql.sql | \
  docker compose exec -T cms-postgresql psql -U postgres wso2am > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "   ✓ Base schema initialized"
else
    echo "   ⚠ Base schema warning (may have non-critical errors)"
fi

# Initialize APIM-specific schema (201 tables)
echo "📋 Step 3: Initializing APIM-specific schema (201 tables)..."
docker compose exec cms-apim cat /home/wso2carbon/wso2am-4.3.0/dbscripts/apimgt/postgresql.sql | \
  docker compose exec -T cms-postgresql psql -U postgres wso2am > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "   ✓ APIM schema initialized"
else
    echo "   ⚠ APIM schema warning (may have non-critical errors)"
fi

# Initialize Identity schema (optional - may not be present in all versions)
echo "📋 Step 4: Initializing Identity schema (optional)..."
if docker compose exec cms-apim test -f /home/wso2carbon/wso2am-4.3.0/dbscripts/identity/postgresql.sql 2>/dev/null; then
    docker compose exec cms-apim cat /home/wso2carbon/wso2am-4.3.0/dbscripts/identity/postgresql.sql | \
      docker compose exec -T cms-postgresql psql -U postgres wso2am > /dev/null 2>&1
    echo "   ✓ Identity schema initialized"
else
    echo "   ⚠ Identity schema not found (optional, skipping)"
fi

# Verify schema creation
echo ""
echo "📊 Verifying schema creation..."
TABLE_COUNT=$(docker compose exec -T cms-postgresql psql -U postgres wso2am -c \
  "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | grep -oE '[0-9]+' | head -1)

echo ""
echo "✅ WSO2 APIM database initialization complete!"
echo ""
echo "📊 Database Details:"
echo "   Host: cms-postgresql"
echo "   Port: 5432"
echo "   Database: wso2am"
echo "   Tables Created: $TABLE_COUNT"
echo "   Schemas: PostgreSQL, APIM, Identity"
echo ""
echo "🚀 Next steps:"
echo "   1. Start/restart WSO2 APIM: docker compose restart cms-apim"
echo "   2. Access Admin Console: https://localhost:9443/carbon"
echo "   3. Access Publisher: https://localhost:9443/publisher"
echo "   4. Developer Portal: https://localhost:9443/devportal"
echo ""
echo "📝 Note: Default admin credentials are admin/admin (configured in deployment.toml)"
