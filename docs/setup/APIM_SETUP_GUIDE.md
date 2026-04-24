# WSO2 API Manager Setup Guide

This guide provides complete instructions for setting up WSO2 API Manager (APIM) 4.3.0 with PostgreSQL database backend.

**Last Updated**: April 24, 2026  
**APIM Version**: 4.3.0  
**Database**: PostgreSQL 15.3  
**Status**: ✅ Production Ready

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Setup](#database-setup)
3. [APIM Container Setup](#apim-container-setup)
4. [Verification & Health Checks](#verification--health-checks)
5. [Troubleshooting](#troubleshooting)
6. [Performance Notes](#performance-notes)

---

## Prerequisites

- Docker & Docker Compose installed
- PostgreSQL container running (`cms-postgresql`)
- Backend API service running (for endpoint testing)
- Ports available: 9443 (APIM Admin/Publisher), 8280 (HTTP Gateway), 8243 (HTTPS Gateway)

---

## Database Setup

### Step 1: Create wso2am Database

```bash
# Drop existing database if needed (for fresh installation)
docker exec cms-postgresql psql -U postgres -c "DROP DATABASE IF EXISTS wso2am;"

# Create new wso2am database
docker exec cms-postgresql psql -U postgres -c "CREATE DATABASE wso2am OWNER postgres;"

echo "✓ Database 'wso2am' created successfully"
```

**Expected Output**: `CREATE DATABASE` or `DROP DATABASE`

---

### Step 2: Load APIM Schema (apimgt_43.sql)

This schema contains all API management tables.

```bash
# Copy schema file to PostgreSQL container
docker cp /home/samehabib/CMS-Platform/apimgt_43.sql cms-postgresql:/tmp/apimgt_43.sql

# Load schema into wso2am database
docker exec cms-postgresql psql -U postgres -d wso2am -f /tmp/apimgt_43.sql

echo "✓ APIM schema loaded successfully"
```

**Expected Result**: 203+ tables created with multiple indexes and constraints

**Verify**:
```bash
docker exec cms-postgresql psql -U postgres -d wso2am -c "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema='public';"
```

**Expected Output**: `203-252` tables (depending on shared.sql)

---

### Step 3: Load Identity/User Management Schema (shared.sql)

This schema creates user management tables required for APIM operations.

```bash
# Copy shared schema file to container
docker cp /home/samehabib/CMS-Platform/wso2-stack/apim/init_db_script/shared.sql cms-postgresql:/tmp/shared.sql

# Load schema into wso2am database
docker exec cms-postgresql psql -U postgres -d wso2am -f /tmp/shared.sql

echo "✓ Identity schema loaded successfully"
```

**Critical Tables Created**:
- `um_domain` - User domain management
- `um_user` - User accounts
- `um_role` - User roles
- `um_permission` - Permissions
- `um_shared_user_role` - User-role mapping

**Verify um_domain exists**:
```bash
docker exec cms-postgresql psql -U postgres -d wso2am -c "SELECT tablename FROM pg_tables WHERE tablename = 'um_domain';"
```

**Expected Output**: 
```
 tablename 
-----------
 um_domain
(1 row)
```

---

## APIM Container Setup

### Step 1: Verify deployment.toml Configuration

Ensure `/home/samehabib/CMS-Platform/wso2-stack/apim/deployment.toml` contains correct database credentials:

```toml
[database.identity_db]
type = "postgres"
url = "jdbc:postgresql://cms-postgresql:5432/wso2am"
username = "postgres"
password = "postgres"
driver = "org.postgresql.Driver"

[database.shared_db]
type = "postgres"
url = "jdbc:postgresql://cms-postgresql:5432/wso2am"
username = "postgres"
password = "postgres"
driver = "org.postgresql.Driver"

[database.apim_db]
type = "postgres"
url = "jdbc:postgresql://cms-postgresql:5432/wso2am"
username = "postgres"
password = "postgres"
driver = "org.postgresql.Driver"
```

---

### Step 2: Start APIM Container

Using Docker Compose:

```bash
cd /home/samehabib/CMS-Platform

# Start APIM container
docker compose up -d cms-apim

# Monitor startup
docker logs -f cms-apim
```

Or restart if already running:

```bash
docker restart cms-apim
```

---

### Step 3: Wait for Full Startup

APIM requires 65-75 seconds to fully initialize:

```bash
# Wait for startup completion
sleep 70

# Verify startup success (check for "Carbon started" message)
docker logs cms-apim 2>&1 | grep "Carbon started"
```

**Expected Output**:
```
[2026-04-24 10:07:10,655]  INFO - StartupFinalizerServiceComponent WSO2 Carbon started in 67 sec
```

---

## Verification & Health Checks

### 1. Check Container Status

```bash
docker ps | grep cms-apim
```

**Expected Status**: `Up X minutes (health: starting)` → `Up X minutes (healthy)`

---

### 2. Verify Database Connectivity

```bash
# Test APIM can reach PostgreSQL
docker exec cms-apim curl -s http://cms-postgresql:5432

# Check database schema tables
docker exec cms-postgresql psql -U postgres -d wso2am -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"
```

---

### 3. Test APIM API Endpoint

```bash
# List all APIs (should return empty list for fresh installation)
curl -s -k -X GET "https://localhost:9443/api/am/publisher/v4/apis" \
  -u "admin:admin" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

**Expected Response**:
```json
{
  "count": 0,
  "list": [],
  "pagination": {...}
}
```

---

### 4. Verify Backend API Connectivity

```bash
# Test from within APIM container
docker exec cms-apim curl -s http://cms-backend:8000/oracle/test

# Expected: JSON response with test data
```

---

### 5. Comprehensive Health Check Script

```bash
#!/bin/bash
echo "=== APIM Health Check ==="
echo ""

echo "1. Container Status:"
docker ps | grep cms-apim | awk '{print "   Status:", $(NF-1)}'
echo ""

echo "2. Database Schema:"
docker exec cms-postgresql psql -U postgres -d wso2am -c "SELECT COUNT(*) as total_tables FROM information_schema.tables WHERE table_schema='public';"
echo ""

echo "3. APIM API Endpoint:"
RESPONSE=$(curl -s -k "https://localhost:9443/api/am/publisher/v4/apis" -u "admin:admin")
if echo "$RESPONSE" | grep -q '"count"'; then
  COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])" 2>/dev/null || echo "ERROR")
  echo "   APIs Registered: $COUNT"
else
  echo "   ERROR: Cannot reach APIM endpoint"
fi
echo ""

echo "4. Backend Connectivity (from APIM):"
if docker exec cms-apim curl -s http://cms-backend:8000/oracle/test | grep -q '"ID"'; then
  echo "   ✓ Backend is reachable"
else
  echo "   ✗ Backend is unreachable"
fi
echo ""

echo "=== All checks complete ==="
```

---

## Troubleshooting

### Issue: "database 'wso2am' does not exist"

**Cause**: Database creation step was skipped  
**Solution**: Run Step 1 of Database Setup section

```bash
docker exec cms-postgresql psql -U postgres -c "CREATE DATABASE wso2am OWNER postgres;"
```

---

### Issue: "ERROR: relation 'um_domain' does not exist"

**Cause**: shared.sql schema was not loaded  
**Solution**: Run Step 3 of Database Setup section

```bash
docker cp /home/samehabib/CMS-Platform/wso2-stack/apim/init_db_script/shared.sql cms-postgresql:/tmp/shared.sql
docker exec cms-postgresql psql -U postgres -d wso2am -f /tmp/shared.sql
docker restart cms-apim
```

---

### Issue: APIM taking too long to start (> 120 seconds)

**Cause**: Database schema not fully loaded  
**Solution**: 
1. Check logs for specific table errors
2. Verify all schema files were loaded completely
3. Increase Docker memory allocation if needed

```bash
docker logs cms-apim 2>&1 | grep -i "error\|exception" | head -10
```

---

### Issue: "NullPointerException" in logs

**Cause**: Key manager configuration missing  
**Solution**: Verify deployment.toml external key manager is disabled or properly configured

```bash
grep -A 10 "key_manager" /home/samehabib/CMS-Platform/wso2-stack/apim/deployment.toml
```

---

## Performance Notes

### Startup Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Container start | 5-10s | Fast |
| Database initialization | 20-30s | Normal |
| APIM service startup | 35-45s | Normal |
| **Total** | **65-75s** | ✅ |

### Database Size

```bash
# Check wso2am database size
docker exec cms-postgresql psql -U postgres -c "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) FROM pg_database WHERE datname = 'wso2am';"
```

### Connection Pool Settings

Default connection pool is configured for:
- **Max connections**: 10
- **Min connections**: 2
- **Connection timeout**: 30s
- **Idle timeout**: 900s

---

## Quick Start (All-in-One)

```bash
#!/bin/bash
set -e

echo "🚀 WSO2 APIM Complete Setup..."
echo ""

# Step 1: Create Database
echo "1️⃣  Creating database..."
docker exec cms-postgresql psql -U postgres -c "DROP DATABASE IF EXISTS wso2am;" 2>/dev/null || true
docker exec cms-postgresql psql -U postgres -c "CREATE DATABASE wso2am OWNER postgres;"

# Step 2: Load APIM Schema
echo "2️⃣  Loading APIM schema (apimgt_43.sql)..."
docker cp /home/samehabib/CMS-Platform/apimgt_43.sql cms-postgresql:/tmp/apimgt_43.sql
docker exec cms-postgresql psql -U postgres -d wso2am -f /tmp/apimgt_43.sql > /dev/null 2>&1

# Step 3: Load Identity Schema
echo "3️⃣  Loading Identity schema (shared.sql)..."
docker cp /home/samehabib/CMS-Platform/wso2-stack/apim/init_db_script/shared.sql cms-postgresql:/tmp/shared.sql
docker exec cms-postgresql psql -U postgres -d wso2am -f /tmp/shared.sql > /dev/null 2>&1

# Step 4: Start APIM
echo "4️⃣  Starting APIM container..."
docker restart cms-apim

# Step 5: Wait and verify
echo "5️⃣  Waiting for APIM startup (70 seconds)..."
sleep 70

# Step 6: Health check
echo "6️⃣  Performing health check..."
RESPONSE=$(curl -s -k "https://localhost:9443/api/am/publisher/v4/apis" -u "admin:admin")
if echo "$RESPONSE" | grep -q '"count"'; then
  echo ""
  echo "✅ WSO2 APIM Setup Complete!"
  echo "   Admin URL: https://localhost:9443"
  echo "   Username: admin"
  echo "   Password: admin"
  echo ""
else
  echo "❌ APIM health check failed. Please check logs:"
  docker logs cms-apim | tail -20
  exit 1
fi
```

Save this as `setup_apim.sh` and run:
```bash
chmod +x setup_apim.sh
./setup_apim.sh
```

---

## Next Steps

After successful setup:

1. **Register Test APIs** → See [API_REGISTRATION_GUIDE.md](API_REGISTRATION_GUIDE.md)
2. **Configure API Policies** → APIM Publisher Console
3. **Setup Subscribers & Applications** → APIM Admin Console
4. **Enable Analytics** → Configure Apim Analytics
5. **Production Deployment** → See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)

---

## Support & Logs

For detailed debugging:

```bash
# View full startup logs
docker logs cms-apim

# Follow live logs
docker logs -f cms-apim

# Extract error logs only
docker logs cms-apim 2>&1 | grep -i "error\|exception" | head -20

# Check database connectivity
docker exec cms-apim curl -v http://cms-postgresql:5432

# Verify schema completeness
docker exec cms-postgresql psql -U postgres -d wso2am -c "\dt" | wc -l
```

---

**Version**: 1.0  
**Last Tested**: April 24, 2026  
**Status**: ✅ All checks passing
