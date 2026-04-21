# jPOS EE Testing Quick Reference Guide

**Date**: April 21, 2026  
**Purpose**: Quick start guide for comprehensive ISO 8583 → Backend API → Database testing

---

## 🚀 Quick Start (5 minutes)

```bash
# 1. Navigate to project
cd /home/samehabib/CMS-Platform

# 2. Ensure services are running
docker-compose up -d

# 3. Run all tests (Phases 1-5)
bash jposee_test_suite.sh 1-5

# 4. View results
# Test summary printed to console
```

---

## 📋 Test Phases Overview

| Phase | Name | Duration | Focus | Status Check |
|-------|------|----------|-------|--------------|
| 1 | Unit Tests | 2 min | API health, DB schema | `curl http://localhost:8000/jposee/monitoring/health` |
| 2 | Integration Tests | 3 min | Create transaction, DB persistence | Transaction in database |
| 3 | End-to-End Tests | 5 min | Authorization flow, filtering | Complete transaction lifecycle |
| 4 | Advanced Tests | 5 min | Batch, concurrent operations | Multiple transaction handling |
| 5 | Monitoring & Analytics | 3 min | Metrics accuracy, audit trails | Dashboard data matches DB |

---

## 🧪 Running Individual Test Phases

### Phase 1: Unit Tests Only
```bash
bash jposee_test_suite.sh 1

# Tests:
# - API health check
# - Database connectivity
# - Table schema validation
```

### Phase 2: Integration Tests
```bash
bash jposee_test_suite.sh 2

# Tests:
# - Create transaction via API
# - Verify transaction in database
# - Check audit log entries
```

### Phase 3: End-to-End Tests
```bash
bash jposee_test_suite.sh 3

# Tests:
# - Authorization flow
# - Transaction filtering
# - Dashboard statistics
```

### Phase 4: Advanced Tests
```bash
bash jposee_test_suite.sh 4

# Tests:
# - Batch transaction creation (10 transactions)
# - Concurrent transaction processing (5 parallel)
```

### Phase 5: Monitoring & Analytics
```bash
bash jposee_test_suite.sh 5

# Tests:
# - Metrics accuracy (DB vs API)
# - Audit trail completeness
# - Query performance (target: <2000ms)
```

### Run Multiple Phases
```bash
# Phases 1, 2, 3
bash jposee_test_suite.sh 1-3

# Phases 2, 4, 5
bash jposee_test_suite.sh 2,4-5

# All phases
bash jposee_test_suite.sh 1-5
```

---

## 🔍 Manual Testing: ISO 8583 → API Flow

### Step 1: Prepare Test Message

```bash
# Create test directory
mkdir -p /tmp/jposee_test

# Create a simple JSON representation of ISO message
cat > /tmp/jposee_test/iso_auth.json << 'EOF'
{
  "mti": "0100",
  "pan": "4532015112830366",
  "processing_code": "000000",
  "amount": 5000,
  "currency": "USD",
  "stan": "000001",
  "transmission_datetime": "2026-04-21T14:30:00Z",
  "merchant_id": "MERCHANT_001",
  "terminal_id": "TERMINAL_001",
  "transaction_type": "PURCHASE"
}
EOF
```

### Step 2: Send to Backend API

```bash
# POST transaction to backend
curl -X POST http://localhost:8000/jposee/transactions/create \
  -H "Content-Type: application/json" \
  -d '{
    "pan": "4532015112830366",
    "processing_code": "000000",
    "amount": 5000,
    "currency": "USD",
    "merchant_id": "MERCHANT_001",
    "terminal_id": "TERMINAL_001",
    "transaction_type": "PURCHASE"
  }' | jq .

# Expected Response:
# {
#   "transaction_id": "TX_20260421_000001",
#   "status": "pending",
#   "created_at": "2026-04-21T14:30:00Z"
# }
```

### Step 3: Verify in Database

```bash
# Get transaction ID from response
TX_ID="TX_20260421_000001"

# Query transaction table
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT id, pan, amount, currency, merchant_id, status, created_at 
   FROM jposee_transactions 
   WHERE id = '$TX_ID';"

# Expected: One row with matching data
```

### Step 4: Verify Audit Trail

```bash
# Check audit logs for transaction lifecycle events
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT action, description, created_at 
   FROM jposee_audit_logs 
   WHERE transaction_id = '$TX_ID' 
   ORDER BY created_at;"

# Expected entries:
# - TRANSACTION_CREATED
# - ROUTING_EVALUATED (if applicable)
# - TRANSACTION_ROUTED
```

### Step 5: Retrieve Transaction via API

```bash
# Get transaction details
curl http://localhost:8000/jposee/transactions/$TX_ID | jq .

# Get filtered transaction list
curl http://localhost:8000/jposee/transactions/list?status=pending | jq .

# Get dashboard summary
curl http://localhost:8000/jposee/monitoring/dashboard | jq .
```

---

## 🔄 Common Test Workflows

### Workflow 1: Simple Authorization Flow
```bash
# 1. Create authorization transaction
TX_ID=$(curl -s -X POST http://localhost:8000/jposee/transactions/create \
  -H "Content-Type: application/json" \
  -d '{
    "pan": "4532015112830366",
    "processing_code": "000000",
    "amount": 5000,
    "currency": "USD",
    "merchant_id": "TEST_001",
    "terminal_id": "TERM_001",
    "transaction_type": "PURCHASE"
  }' | jq -r '.transaction_id')

echo "Created transaction: $TX_ID"

# 2. Update status to APPROVED
curl -s -X PATCH http://localhost:8000/jposee/transactions/$TX_ID \
  -H "Content-Type: application/json" \
  -d '{"status": "APPROVED"}' | jq .

# 3. Verify in database
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT id, status FROM jposee_transactions WHERE id = '$TX_ID';"

# 4. Check complete audit trail
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT action FROM jposee_audit_logs WHERE transaction_id = '$TX_ID' ORDER BY created_at;"
```

### Workflow 2: Batch Transaction Testing
```bash
# 1. Create 10 transactions
for i in {1..10}; do
  curl -s -X POST http://localhost:8000/jposee/transactions/create \
    -H "Content-Type: application/json" \
    -d "{
      \"pan\": \"4532015112830366\",
      \"processing_code\": \"000000\",
      \"amount\": $((5000 + i * 100)),
      \"currency\": \"USD\",
      \"merchant_id\": \"BATCH_001\",
      \"terminal_id\": \"TERM_BATCH\",
      \"transaction_type\": \"PURCHASE\"
    }" > /tmp/tx_$i.json
done

# 2. Count created transactions
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT COUNT(*) FROM jposee_transactions WHERE merchant_id = 'BATCH_001';"

# 3. Calculate average amount
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT AVG(amount), MIN(amount), MAX(amount) 
   FROM jposee_transactions 
   WHERE merchant_id = 'BATCH_001';"
```

### Workflow 3: Concurrent Load Test
```bash
# Create 20 concurrent transactions
for i in {1..20}; do
  curl -s -X POST http://localhost:8000/jposee/transactions/create \
    -H "Content-Type: application/json" \
    -d "{
      \"pan\": \"4532015112830366\",
      \"processing_code\": \"000000\",
      \"amount\": $((1000 + RANDOM % 9000)),
      \"currency\": \"USD\",
      \"merchant_id\": \"CONCURRENT_$i\",
      \"terminal_id\": \"TERM_CONC_$i\",
      \"transaction_type\": \"PURCHASE\"
    }" &
done

wait

# Check all transactions created successfully
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT COUNT(DISTINCT merchant_id) FROM jposee_transactions 
   WHERE merchant_id LIKE 'CONCURRENT_%';"

# Check for duplicates (should be 0)
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT transaction_id FROM jposee_transactions 
   GROUP BY transaction_id 
   HAVING COUNT(*) > 1;"
```

---

## 📊 Monitoring & Verification

### Check System Health
```bash
# API Health
curl http://localhost:8000/jposee/monitoring/health | jq .

# Docker Container Status
docker ps --filter "name=jposee-db|name=cms-backend" --format "table {{.Names}}\t{{.Status}}"

# Database Connections
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT datname, usename, count(*) FROM pg_stat_activity GROUP BY datname, usename;"
```

### View Transaction Summary
```bash
# Total transactions by status
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT status, COUNT(*) as count 
   FROM jposee_transactions 
   GROUP BY status 
   ORDER BY count DESC;"

# Transactions by merchant
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT merchant_id, COUNT(*) as count, SUM(amount) as total_amount 
   FROM jposee_transactions 
   GROUP BY merchant_id 
   ORDER BY count DESC LIMIT 10;"

# Recent transactions
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT id, pan, amount, status, created_at 
   FROM jposee_transactions 
   ORDER BY created_at DESC LIMIT 10;"
```

### View Dashboard Summary
```bash
# Get comprehensive dashboard stats
curl http://localhost:8000/jposee/monitoring/dashboard | jq '{
  total_transactions: .total_transactions,
  approved_count: .approved_count,
  declined_count: .declined_count,
  pending_count: .pending_count,
  success_rate_percent: .success_rate_percent,
  avg_response_time_ms: .avg_response_time_ms
}'
```

---

## 🛠️ Troubleshooting

### Backend API Not Responding
```bash
# Check if backend container is running
docker ps | grep cms-backend

# View backend logs
docker logs cms-backend | tail -50

# Restart backend
docker restart cms-backend

# Verify health
sleep 3 && curl http://localhost:8000/jposee/monitoring/health
```

### Database Connection Issues
```bash
# Check database container
docker ps | grep jposee-db

# Test direct connection
docker exec jposee-db psql -U postgres -d jposee -c "SELECT 1 AS test;"

# Check table structure
docker exec jposee-db psql -U postgres -d jposee -c "\d jposee_transactions"

# Verify data
docker exec jposee-db psql -U postgres -d jposee -c "SELECT COUNT(*) FROM jposee_transactions;"
```

### Test Suite Failures
```bash
# Run with verbose output
bash jposee_test_suite.sh 1 --verbose

# Check individual component
curl -v http://localhost:8000/jposee/monitoring/health

# Validate docker network
docker network ls
docker network inspect cms-platform-net

# Check service connectivity
docker exec cms-backend ping jposee-db
```

---

## 📈 Performance Benchmarking

### Throughput Test (transactions/second)
```bash
#!/bin/bash
# Save as throughput_test.sh

START=$(date +%s%N)
COUNT=0

for i in {1..100}; do
  curl -s -X POST http://localhost:8000/jposee/transactions/create \
    -H "Content-Type: application/json" \
    -d "{
      \"pan\": \"4532015112830366\",
      \"amount\": $((RANDOM % 10000)),
      \"currency\": \"USD\",
      \"merchant_id\": \"PERF_$i\",
      \"terminal_id\": \"TERM_PERF\",
      \"transaction_type\": \"PURCHASE\"
    }" > /dev/null 2>&1 &
  COUNT=$((COUNT + 1))
done

wait

END=$(date +%s%N)
DURATION=$(( (END - START) / 1000000000 ))

THROUGHPUT=$((COUNT / DURATION))
echo "Throughput: $THROUGHPUT transactions/second"
```

### Response Time Test
```bash
#!/bin/bash
# Save as response_time_test.sh

TOTAL_TIME=0
SAMPLES=50

for i in $(seq 1 $SAMPLES); do
  START=$(date +%s%N)
  
  curl -s http://localhost:8000/jposee/transactions/list?limit=10 > /dev/null
  
  END=$(date +%s%N)
  ELAPSED=$(( (END - START) / 1000000 ))
  
  TOTAL_TIME=$((TOTAL_TIME + ELAPSED))
  echo "Sample $i: ${ELAPSED}ms"
done

AVG=$((TOTAL_TIME / SAMPLES))
echo "Average response time: ${AVG}ms"
```

---

## 📝 Test Results Template

```
═════════════════════════════════════════════════════════
           jPOS EE TEST RESULTS
═════════════════════════════════════════════════════════

Test Date: 2026-04-21
Test Time: 14:30:00 UTC
Tester: [Your Name]
Environment: Development

─────────────────────────────────────────────────────
SUMMARY
─────────────────────────────────────────────────────

Total Tests: 23
Passed: 23
Failed: 0
Pass Rate: 100%

─────────────────────────────────────────────────────
PHASE RESULTS
─────────────────────────────────────────────────────

Phase 1 - Unit Tests: ✅ PASS (3/3)
  ✅ API Health Check
  ✅ Database Connectivity
  ✅ Schema Validation

Phase 2 - Integration: ✅ PASS (3/3)
  ✅ Create Transaction
  ✅ Database Persistence
  ✅ Audit Logging

Phase 3 - E2E: ✅ PASS (3/3)
  ✅ Authorization Flow
  ✅ Transaction Filtering
  ✅ Dashboard Stats

Phase 4 - Advanced: ✅ PASS (2/2)
  ✅ Batch Creation (10/10)
  ✅ Concurrent Processing (5/5)

Phase 5 - Monitoring: ✅ PASS (3/3)
  ✅ Metrics Accuracy
  ✅ Audit Trail
  ✅ Query Performance

─────────────────────────────────────────────────────
PERFORMANCE METRICS
─────────────────────────────────────────────────────

Avg Response Time: 245ms
Max Response Time: 1847ms
Throughput: 487 tx/sec
Database Queries: All < 2000ms
Error Rate: 0%

─────────────────────────────────────────────────────
CONCLUSION
─────────────────────────────────────────────────────

✅ All tests passed successfully
✅ System ready for staging deployment
✅ Performance within acceptable ranges
✅ Data integrity verified
✅ Audit trail complete

═════════════════════════════════════════════════════════
```

---

## 🔗 Related Documentation

- [JPOSEE_E2E_TESTING_PLAN.md](JPOSEE_E2E_TESTING_PLAN.md) - Comprehensive testing plan
- [JPOSEE_POSTGRES_SETUP_GUIDE.md](JPOSEE_POSTGRES_SETUP_GUIDE.md) - Database setup
- [JPOSEE_UI_DEVELOPMENT_PLAN.md](JPOSEE_UI_DEVELOPMENT_PLAN.md) - UI development
- [SETUP_NEW_SERVER.md](SETUP_NEW_SERVER.md) - New server deployment
- [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) - Production deployment

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review logs: `docker logs cms-backend` / `docker logs jposee-db`
3. Run diagnostics: `bash jposee_test_suite.sh 1 --verbose`
4. Consult [JPOSEE_E2E_TESTING_PLAN.md](JPOSEE_E2E_TESTING_PLAN.md) for detailed information

---

**Document Version**: 1.0  
**Created**: April 21, 2026  
**Last Updated**: April 21, 2026
