# jPOS EE PostgreSQL Persistence Layer - Setup Guide

**Date**: April 21, 2026  
**Status**: Database Schema & Persistence Layer Complete  
**Next Step**: Run migrations on PostgreSQL

---

## 📋 What Was Created

### 1. **Database Schema** (`backend/migrations/001_create_jposee_schema.sql`)
Complete PostgreSQL schema with:
- **jposee_transactions**: Transaction records with ISO 8583 fields
- **jposee_routing_rules**: Routing rules configuration with criteria & actions
- **jposee_audit_logs**: Comprehensive audit trail for all actions
- **jposee_batch_jobs**: Batch job management and tracking
- **jposee_batch_results**: Results for individual batch records
- **jposee_alert_config**: System alert thresholds and settings
- **jposee_metrics**: Performance metrics snapshots
- **jposee_alerts_history**: Alert history and resolution tracking
- **jposee_system_info**: System metadata and version info

**Key Features**:
- ✅ JSONB fields for flexible data storage
- ✅ Comprehensive indexing for performance
- ✅ Foreign key relationships for referential integrity
- ✅ Views for common queries (dashboard stats, active alerts)
- ✅ Automatic timestamps and audit fields

---

### 2. **Pydantic Schemas** (`backend/app/schemas/jposee_schemas.py`)
Complete type-safe request/response models:

**Enums**:
- `TransactionStatus`: success, failed, pending, reversed
- `TransactionType`: Purchase, Refund, Transfer, Reversal, Inquiry, Balance
- `BatchJobStatus`: pending, running, completed, failed, cancelled
- `ActionResult`: SUCCESS, FAILURE, PARTIAL
- `AlertLevel`: info, warning, error, critical

**Request/Response Models**:
- `TransactionCreate`, `TransactionResponse`, `TransactionUpdate`, `TransactionListResponse`
- `RoutingRuleCreate`, `RoutingRuleResponse`, `RoutingRuleUpdate`, `RoutingRuleListResponse`
- `RouteTestRequest`, `RouteTestResponse`, `RoutingAnalyticsResponse`
- `AuditLogCreate`, `AuditLogResponse`, `AuditLogListResponse`
- `BatchJobCreate`, `BatchJobResponse`, `BatchJobListResponse`
- `AlertHistoryResponse`, `AlertConfigResponse`
- `DashboardStatsResponse`, `SystemHealthResponse`, `MetricsSnapshot`

---

### 3. **Database Operations Class** (`backend/app/database/jposee.py`)
`JposEEDB` class with methods for:

**Transactions**:
- `create_transaction(data)` - Create new transaction
- `get_transaction_by_id(id)` - Get transaction by database ID
- `get_transaction_by_txn_id(txn_id)` - Get transaction by transaction ID
- `list_transactions(filters)` - List with pagination & filtering
- `update_transaction(id, data)` - Update transaction status, response, etc.

**Routing Rules**:
- `create_routing_rule(data)` - Create new rule
- `get_routing_rule(id)` - Get rule by ID
- `list_routing_rules(filters)` - List with pagination
- `update_routing_rule(id, data)` - Update rule criteria/action
- `delete_routing_rule(id)` - Delete rule

**Audit Logs**:
- `create_audit_log(data)` - Log action
- `list_audit_logs(filters)` - Query audit logs with filters

**Batch Jobs**:
- `create_batch_job(data)` - Create batch job
- `get_batch_job(id)` - Get job details
- `list_batch_jobs(filters)` - List jobs with pagination
- `update_batch_job(id, data)` - Update job status/progress

**Monitoring**:
- `get_dashboard_stats()` - Dashboard statistics
- `get_routing_analytics()` - Routing rules analytics

---

### 4. **API Routes** (`backend/app/routers/jposee.py`)

**Transaction Endpoints**:
```
GET    /jposee/transactions              - List transactions (paginated)
GET    /jposee/transactions/{id}         - Get transaction by ID
POST   /jposee/transactions              - Create transaction
PUT    /jposee/transactions/{id}         - Update transaction
POST   /jposee/transactions/{id}/retry   - Retry failed transaction
```

**Routing Endpoints**:
```
GET    /jposee/routing/rules             - List routing rules
GET    /jposee/routing/rules/{id}        - Get rule by ID
POST   /jposee/routing/rules             - Create rule
PUT    /jposee/routing/rules/{id}        - Update rule
DELETE /jposee/routing/rules/{id}        - Delete rule
POST   /jposee/routing/test              - Test route matching
GET    /jposee/routing/analytics         - Get routing analytics
```

**Audit Endpoints**:
```
GET    /jposee/audit/logs                - List audit logs
POST   /jposee/audit/logs                - Create audit log
```

**Batch Endpoints**:
```
GET    /jposee/batch/jobs                - List batch jobs
GET    /jposee/batch/jobs/{id}           - Get job details
POST   /jposee/batch/jobs                - Create job
PUT    /jposee/batch/jobs/{id}           - Update job
```

**Monitoring Endpoints**:
```
GET    /jposee/monitoring/dashboard      - Dashboard statistics
GET    /jposee/monitoring/health         - System health status
```

---

## 🚀 Setup Instructions

### Step 1: Run Database Migrations

Connect to PostgreSQL and execute the schema:

```bash
# Using psql
psql -h cms-postgresql -U postgres -d cms -f backend/migrations/001_create_jposee_schema.sql

# Or from within a Docker container
docker exec cms-postgresql psql -U postgres -d cms -f /path/to/001_create_jposee_schema.sql
```

### Step 2: Verify Tables Created

```bash
# Connect to PostgreSQL
psql -h cms-postgresql -U postgres -d cms

# List tables
\dt jposee*

# Should show:
# - jposee_transactions
# - jposee_routing_rules
# - jposee_audit_logs
# - jposee_batch_jobs
# - jposee_batch_results
# - jposee_alert_config
# - jposee_metrics
# - jposee_alerts_history
# - jposee_system_info
```

### Step 3: Backend Already Updated

The backend is already integrated with the new jPOS EE persistence layer:

- ✅ `app/database/jposee.py` - Database operations class
- ✅ `app/routers/jposee.py` - API endpoints
- ✅ `app/schemas/jposee_schemas.py` - Request/response models
- ✅ `app/__init__.py` - Router registered
- ✅ `app/routers/__init__.py` - Router imported
- ✅ `app/database/__init__.py` - JposEEDB exported
- ✅ `app/schemas/__init__.py` - Schemas exported

### Step 4: Start Backend and Test

```bash
# Install dependencies (if needed)
pip install -r backend/requirements.txt

# Start backend
python backend/run.py

# Backend will be available at: http://localhost:8000

# Test endpoints with curl or Postman:
curl http://localhost:8000/jposee/monitoring/dashboard
curl http://localhost:8000/jposee/routing/rules
curl http://localhost:8000/jposee/audit/logs
```

### Step 5: Check API Documentation

Once backend is running, visit:
```
http://localhost:8000/docs
```

You'll see all jPOS EE endpoints with:
- Full documentation
- Try-it-out functionality
- Request/response schemas
- Example data

---

## 📊 Table Structure Summary

### jposee_transactions
```
id                 SERIAL PRIMARY KEY
txn_id            VARCHAR(50) UNIQUE       - Unique transaction identifier
txn_type          VARCHAR(20)              - Purchase, Refund, Transfer, etc.
amount            DECIMAL(15,2)            - Transaction amount
currency          VARCHAR(3)               - Currency code (USD, EUR, etc.)
status            VARCHAR(20)              - success, failed, pending, reversed
timestamp         TIMESTAMP                - Transaction timestamp
card_last4        VARCHAR(4)               - Last 4 digits of card
card_bin          VARCHAR(6)               - Bank Identification Number
merchant_id       VARCHAR(50)              - Merchant identifier
merchant_name     VARCHAR(255)             - Merchant name
merchant_category VARCHAR(50)              - Merchant category code
iso_fields        JSONB                    - Full ISO 8583 message fields
routing_info      JSONB                    - Routing configuration
gateway_response  JSONB                    - Gateway response details
duration_ms       INTEGER                  - Processing time in milliseconds
retry_count       INTEGER                  - Number of retries
```

### jposee_routing_rules
```
id                 SERIAL PRIMARY KEY
rule_name         VARCHAR(255) UNIQUE      - Unique rule name
rule_description  TEXT                     - Rule description
enabled           BOOLEAN                  - Is rule active
priority          INTEGER                  - Higher = higher priority
criteria          JSONB                    - Match criteria (amount, BIN, type, etc.)
action            JSONB                    - Action configuration (route, timeout, etc.)
hit_count         INTEGER                  - Times rule has matched
success_count     INTEGER                  - Successful transactions
failed_count      INTEGER                  - Failed transactions
total_duration_ms INTEGER                  - Cumulative processing time
```

### jposee_audit_logs
```
id                 SERIAL PRIMARY KEY
action_type       VARCHAR(50)              - LOGIN, RULE_CREATED, TXN_PROCESSED, etc.
user_id           INTEGER                  - User who performed action
username          VARCHAR(100)             - Username
ip_address        INET                     - IP address of request
user_agent        TEXT                     - User agent string
resource_type     VARCHAR(50)              - Type of resource (Rule, Transaction, etc.)
resource_id       VARCHAR(100)             - ID of resource
result            VARCHAR(20)              - SUCCESS, FAILURE, PARTIAL
error_message     TEXT                     - Error details if failed
details           JSONB                    - Action-specific details
changes           JSONB                    - Before/after comparison
timestamp         TIMESTAMP                - When action occurred
```

---

## 🔌 Example API Calls

### Create Transaction
```bash
curl -X POST http://localhost:8000/jposee/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "txn_id": "TXN123456",
    "txn_type": "Purchase",
    "amount": 99.99,
    "currency": "USD",
    "status": "success",
    "card_last4": "4567",
    "card_bin": "411111",
    "merchant_id": "MERCH001",
    "merchant_name": "Example Store",
    "duration_ms": 250
  }'
```

### Create Routing Rule
```bash
curl -X POST http://localhost:8000/jposee/routing/rules \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "High-Value Transactions",
    "rule_description": "Route transactions over $1000 to premium gateway",
    "enabled": true,
    "priority": 1,
    "criteria": {
      "amount_min": 1000,
      "bin_ranges": ["411111-411199"]
    },
    "action": {
      "route": "premium_gateway",
      "timeout_ms": 5000
    }
  }'
```

### List Transactions
```bash
curl "http://localhost:8000/jposee/transactions?page=1&limit=10&status=success"
```

### Create Audit Log
```bash
curl -X POST http://localhost:8000/jposee/audit/logs \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "RULE_CREATED",
    "username": "admin",
    "resource_type": "RoutingRule",
    "resource_id": "RULE001",
    "result": "SUCCESS"
  }'
```

---

## ✅ Verification Checklist

- [ ] PostgreSQL running on port 5432
- [ ] Database `cms` created
- [ ] Migration script executed successfully
- [ ] All 9 jPOS EE tables created
- [ ] Backend Python dependencies installed
- [ ] Backend server started (`python run.py`)
- [ ] Endpoints accessible at `http://localhost:8000/jposee/*`
- [ ] API documentation available at `http://localhost:8000/docs`
- [ ] Can create transactions via `/jposee/transactions` POST
- [ ] Can retrieve transactions via `/jposee/transactions` GET

---

## 📚 File Manifest

```
backend/
├── migrations/
│   └── 001_create_jposee_schema.sql        ✅ Database schema
├── app/
│   ├── database/
│   │   ├── jposee.py                       ✅ JposEEDB operations class
│   │   └── __init__.py                     ✅ Updated with jposee_db export
│   ├── routers/
│   │   ├── jposee.py                       ✅ jPOS EE API endpoints
│   │   └── __init__.py                     ✅ Updated with jposee import
│   ├── schemas/
│   │   ├── jposee_schemas.py               ✅ All Pydantic models
│   │   └── __init__.py                     ✅ Updated with exports
│   └── __init__.py                         ✅ Updated with jposee router
└── run.py                                   ✅ No changes needed
```

---

## 🎯 Next Steps

1. **Run Migrations** - Execute SQL schema on PostgreSQL
2. **Test Endpoints** - Use Postman or curl to test API
3. **Verify Data Persistence** - Create records and query database
4. **Frontend Integration** - Build React components for jPOS EE UI (Phase 1)
5. **Real-time Updates** - Implement WebSocket for live monitoring (Phase 6)

---

## 📝 Notes

- All endpoints use pagination (page, limit parameters)
- JSON responses include structured error messages
- Database credentials from `backend/.env` file
- All timestamps stored in UTC with timezone
- JSONB fields allow flexible schema evolution
- Indexes optimized for common queries (status, timestamp, user_id)
- Views provide convenient access to aggregated data

---

**Created**: April 21, 2026  
**Status**: Ready for PostgreSQL Migration  
**Documentation**: Complete
