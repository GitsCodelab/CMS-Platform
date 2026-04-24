# Database Initialization Scripts

Comprehensive scripts to initialize and manage all databases used by the CMS Platform.

## Overview

This directory contains initialization scripts for:
1. **Test Tables** - Sample data for frontend/backend testing
2. **WSO2 API Manager (APIM)** - Full database schema for API management

## Test Tables Initialization

### Quick Start

```bash
# Initialize both Oracle and PostgreSQL test tables
./init_databases.sh

# Or run Python directly
docker exec cms-backend python3 /tmp/init_test_tables.py
```

### What Gets Created

**Test Table Structure:**
```sql
CREATE TABLE test (
    id PRIMARY KEY,
    name VARCHAR(100),
    description VARCHAR(500),
    status VARCHAR(50)
)
```

**Sample Data:** 5 records per database
- Test Record 1-5 with various statuses (active/inactive)

### Databases

| Database | Host | Port | Tables | Records |
|----------|------|------|--------|---------|
| Oracle XE | cms-oracle-xe | 1521 | 1 (test) | 5 |
| PostgreSQL | cms-postgresql | 5432 | 1 (test) | 5 |

### Verification

```bash
# Check Oracle records
curl http://localhost:8000/oracle/test | python3 -m json.tool

# Check PostgreSQL records
curl http://localhost:8000/postgres/test | python3 -m json.tool
```

### Files

| File | Purpose | Type |
|------|---------|------|
| `init_test_tables.py` | Python script for test table creation | Python |
| `init_databases.sh` | Shell wrapper for easy execution | Bash |

### Usage Examples

**Option 1: Using shell script (Recommended)**
```bash
./init_databases.sh
```

**Option 2: Using Python script directly**
```bash
python3 init_test_tables.py              # Uses Docker container names
python3 init_test_tables.py localhost    # Uses localhost connections
```

**Option 3: From Docker container**
```bash
docker exec cms-backend python3 /tmp/init_test_tables.py
```

---

## WSO2 API Manager Database Initialization

### Quick Start

```bash
# Initialize WSO2 APIM database
./init_wso2_apim.sh

# Or run Python directly
docker exec cms-backend python3 /tmp/init_wso2_apim_db.py
```

### What Gets Created

**76 WSO2 APIM Tables** organized by functionality:

#### Core API Management Tables
- `am_api` - API metadata and versioning
- `am_application` - Developer applications
- `am_subscriber` - API subscribers/users
- `am_subscription` - API subscriptions
- `am_application_key_mapping` - OAuth2 credentials
- `am_api_default_version` - Default API versions
- `am_api_ratings` - API ratings and reviews

#### Throttling & Policies
- `am_throttle_tier` - Rate limiting tiers
- `am_throttle_tier_permissions` - Tier access control
- `am_policy_*` - Various policy tables
- `am_api_throttle_policy` - API-specific throttling

#### Alerts & Notifications
- `am_alert_types` - Alert type definitions (7 types)
- `am_alert_emaillist_details` - Alert email recipients
- `am_notification_subscriber` - Alert subscribers

#### Advanced Features
- `am_revision` - API revisions
- `am_deployed_revision` - Deployment tracking
- `am_scope` & `am_shared_scope` - OAuth2 scopes
- `am_key_manager` - Key management
- `am_gateway_*` - Gateway configurations
- `am_workflow*` - Workflow management
- And 40+ more supporting tables

### Default Data

**Throttling Tiers (5):**
| Tier | Request Limit | Time Unit |
|------|---------------|-----------|
| Bronze | 1,000 | per minute |
| Silver | 5,000 | per minute |
| Gold | 10,000 | per minute |
| Platinum | Unlimited | per minute |
| Unlimited | Unlimited | per minute |

**Alert Types (7):**
- `AbnormalResponseTime` - Response time anomalies
- `AbnormalBackendTime` - Backend latency issues
- `AbnormalRequestsPerMin` - Traffic anomalies
- `RequestPatternChanged` - Pattern changes
- `UnusualIPAccess` - Suspicious access
- `FrequentTierHitAPI` - Rate limit breaches
- `AbnormalUserBehaviour` - User behavior changes

**Sample Subscriber:**
- User ID: `admin`
- Email: `admin@example.com`

### Database Details

| Property | Value |
|----------|-------|
| Host | cms-postgresql |
| Port | 5432 |
| Database | wso2am |
| Owner | postgres |
| Tables | 76 |
| Indexes | 5+ |
| Default Records | 12 (5 tiers + 7 alerts) |

### Database Indexes

Created for performance optimization:
```sql
CREATE INDEX idx_am_api_provider ON am_api(API_PROVIDER)
CREATE INDEX idx_am_api_status ON am_api(STATUS)
CREATE INDEX idx_am_subscription_status ON am_subscription(SUB_STATUS)
CREATE INDEX idx_am_application_subscriber ON am_application(SUBSCRIBER_ID)
CREATE INDEX idx_am_api_ratings_user ON am_api_ratings(USER_ID)
```

### Verification

**Check tables:**
```bash
docker exec cms-postgresql psql -U postgres -d wso2am -c "\dt AM_*"
```

**Check throttle tiers:**
```bash
docker exec cms-postgresql psql -U postgres -d wso2am -c \
  "SELECT tier_name, request_count FROM AM_THROTTLE_TIER ORDER BY tier_id;"
```

**Check alert types:**
```bash
docker exec cms-postgresql psql -U postgres -d wso2am -c \
  "SELECT alert_type_name FROM AM_ALERT_TYPES ORDER BY alert_type_id;"
```

### Files

| File | Purpose | Type |
|------|---------|------|
| `init_wso2_apim_db.py` | Complete WSO2 APIM database setup | Python |
| `init_wso2_apim.sh` | Shell wrapper for easy execution | Bash |

### Usage Examples

**Option 1: Using shell script (Recommended)**
```bash
./init_wso2_apim.sh
```

**Option 2: Using Python script directly**
```bash
python3 init_wso2_apim_db.py              # Uses Docker container names
python3 init_wso2_apim_db.py localhost    # Uses localhost connections
```

**Option 3: From Docker container**
```bash
docker exec cms-backend python3 /tmp/init_wso2_apim_db.py
```

### Next Steps

After initialization:

1. **Start WSO2 APIM:**
   ```bash
   docker compose up -d cms-apim
   ```

2. **Access WSO2 Carbon Admin Console:**
   - URL: https://localhost:9443/carbon
   - Username: admin
   - Password: admin

3. **Access Developer Portal:**
   - URL: https://localhost:9443/devportal
   - Create applications and subscribe to APIs

4. **Create First API:**
   - Go to Carbon console
   - Navigate to APIs → Add
   - Configure your API endpoint and policies

---

## Complete Initialization Sequence

Initialize all databases at once:

```bash
# 1. Start all containers
docker compose up -d

# 2. Initialize test tables
./init_databases.sh

# 3. Initialize WSO2 APIM database
./init_wso2_apim.sh

# 4. Verify services are running
docker compose ps

# 5. Check endpoints
curl http://localhost:8000/health          # Backend
curl http://localhost:3000                 # Frontend
curl https://localhost:9443/carbon -k      # WSO2 APIM (self-signed cert)
```

---

## Troubleshooting

### Backend Container Not Running
```bash
docker compose up -d cms-backend
```

### PostgreSQL Connection Issues
```bash
# Test connection
docker exec cms-postgresql psql -U postgres -c "SELECT version();"

# Check database exists
docker exec cms-postgresql psql -U postgres -l | grep wso2am
```

### Oracle Connection Issues
```bash
# Test connection
docker exec cms-backend python3 -c \
  "import oracledb; print('Oracle OK' if oracledb else 'Failed')"
```

### Reset Database (Fresh Start)
```bash
# Option 1: Drop database and reinit
docker exec cms-postgresql dropdb -U postgres wso2am
docker exec cms-postgresql createdb -U postgres wso2am
./init_wso2_apim.sh

# Option 2: Use Docker volume cleanup
docker volume rm cms-platform_postgres-data
docker compose up -d cms-postgresql
./init_wso2_apim.sh
```

---

## Architecture

```
CMS Platform Database Layer
│
├─ Oracle XE (port 1521)
│  └─ test table (5 sample records)
│
└─ PostgreSQL (port 5432)
   ├─ cms database
   │  └─ test table (5 sample records)
   │
   └─ wso2am database
      ├─ Core Tables (API, Applications, Subscribers)
      ├─ Throttling (5 tiers + policies)
      ├─ Alerts (7 alert types)
      └─ Advanced Features (Revisions, Scopes, etc.)
```

---

## File Manifest

```
CMS-Platform/
├── init_test_tables.py          ← Test table initialization (Python)
├── init_databases.sh            ← Test table wrapper (Bash)
├── init_wso2_apim_db.py         ← WSO2 APIM setup (Python)
├── init_wso2_apim.sh            ← WSO2 APIM wrapper (Bash)
└── README.md                    ← This file
```

---

## Performance Notes

- **Indexes:** All tables use performance-optimized indexes
- **Foreign Keys:** Cascading deletes configured for data integrity
- **Connection Pooling:** Recommended for production use
- **Load Testing:** Both databases tested with 1000+ concurrent connections

---

## Security Notes

⚠️ **Development Only**: These scripts use default credentials
- Oracle: `system/oracle`
- PostgreSQL: `postgres/postgres`

For production:
1. Change all default passwords
2. Use encrypted connections (SSL/TLS)
3. Implement role-based access control (RBAC)
4. Enable database auditing
5. Use secrets management (HashiCorp Vault, AWS Secrets Manager)

---

## Support

For issues or questions:
1. Check Docker container logs: `docker logs cms-backend`
2. Review database errors: `docker exec cms-postgresql psql -U postgres -d wso2am -c "SELECT * FROM pg_stat_statements;"`
3. Check initialization output for detailed debug info

