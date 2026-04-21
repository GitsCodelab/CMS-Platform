# CMS Platform - Production Deployment Guide

Enterprise-grade deployment procedures for CMS Platform in production environments.

## Pre-Deployment Checklist

### Security Review
- [ ] All default passwords changed
- [ ] SSL/TLS certificates installed
- [ ] Firewall rules configured
- [ ] Network segmentation implemented
- [ ] SSH key-based authentication only
- [ ] API rate limiting configured
- [ ] CORS policies configured
- [ ] SQL injection protection verified
- [ ] XSS protection enabled
- [ ] CSRF tokens implemented

### Infrastructure Requirements
- [ ] 4+ CPU cores available
- [ ] 16GB+ RAM available
- [ ] 100GB+ SSD storage
- [ ] Dedicated database servers (optional but recommended)
- [ ] Load balancer configured (if multi-node)
- [ ] Reverse proxy configured (nginx/HAProxy)
- [ ] Monitoring stack deployed
- [ ] Backup system configured
- [ ] CDN configured (for frontend assets)

### Network Configuration
- [ ] DNS records configured
- [ ] SSL/TLS certificate provisioned
- [ ] VPC/Security groups configured
- [ ] Network ACLs configured
- [ ] DDoS protection enabled
- [ ] WAF rules configured

## Production Architecture

### Recommended Multi-Node Setup

```
┌─────────────────────────────────────────────────────────────┐
│                     PRODUCTION ENVIRONMENT                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Load Balancer / Reverse Proxy             │   │
│  │         (nginx/HAProxy/AWS ALB)                     │   │
│  │  Port 80 (HTTP) → 443 (HTTPS)                       │   │
│  └────────┬────────────────────────────┬───────────────┘   │
│           │                            │                   │
│  ┌────────▼──────────┐     ┌───────────▼──────────┐       │
│  │  Backend Server 1 │     │  Backend Server 2    │       │
│  │  (FastAPI)        │     │  (FastAPI)           │       │
│  │  Port 8000        │     │  Port 8000           │       │
│  └────────┬──────────┘     └───────────┬──────────┘       │
│           │                            │                   │
│           └────────────┬───────────────┘                   │
│                        │                                   │
│        ┌───────────────┼───────────────┐                  │
│        │               │               │                  │
│  ┌─────▼───────┐  ┌───▼────────┐  ┌──▼──────────┐       │
│  │  PostgreSQL │  │  jposee-db │  │   Oracle    │       │
│  │  (Platform) │  │ (Payments) │  │   (Legacy)  │       │
│  │  Primary    │  │  Primary   │  │   Standby   │       │
│  └─────┬───────┘  └───┬────────┘  └──┬──────────┘       │
│        │               │               │                 │
│  ┌─────▼───────┐  ┌───▼────────┐  ┌──▼──────────┐       │
│  │  PostgreSQL │  │  jposee-db │  │   Oracle    │       │
│  │  (Platform) │  │ (Payments) │  │   (Legacy)  │       │
│  │  Standby    │  │  Standby   │  │   Standby2  │       │
│  └─────────────┘  └────────────┘  └─────────────┘       │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │       Monitoring, Backup & Logging Services        │   │
│  │  • Prometheus + Grafana (Metrics)                  │   │
│  │  • ELK Stack / Splunk (Logs)                       │   │
│  │  • Backup service (Daily snapshots)                │   │
│  │  • Alert Manager (PagerDuty/Slack integration)     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Environment-Specific Configuration

### Development (.env.development)
```env
# Debug mode enabled
DEBUG=true
LOG_LEVEL=debug

# Local database
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=jposee_dev
POSTGRES_USER=postgres
POSTGRES_PASSWORD=dev_password

# API Configuration
API_TITLE=CMS Platform API (Dev)
WORKERS=1
```

### Staging (.env.staging)
```env
# Debug mode disabled
DEBUG=false
LOG_LEVEL=info

# Staging database
POSTGRES_HOST=staging-db.internal
POSTGRES_PORT=5432
POSTGRES_DB=jposee_staging
POSTGRES_USER=postgres
POSTGRES_PASSWORD=${STAGING_DB_PASSWORD}  # Use secrets manager

# API Configuration
API_TITLE=CMS Platform API (Staging)
WORKERS=4
```

### Production (.env.production)
```env
# Debug mode disabled
DEBUG=false
LOG_LEVEL=warn

# Production database (managed service)
POSTGRES_HOST=prod-jposee-db.us-east-1.rds.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_DB=jposee_prod
POSTGRES_USER=jposee_prod
POSTGRES_PASSWORD=${PROD_DB_PASSWORD}  # Use AWS Secrets Manager

# API Configuration
API_TITLE=CMS Platform API (Production)
WORKERS=8

# Security
ALLOWED_HOSTS=api.cms-platform.com,www.cms-platform.com
CORS_ORIGINS=https://cms-platform.com,https://www.cms-platform.com
```

## Deployment Steps

### 1. Pre-Deployment Testing

```bash
# Run full test suite
bash /tmp/test_jposee_apis.sh

# Performance testing
apache2-utils ab -n 1000 -c 10 http://localhost:8000/jposee/monitoring/health

# Security scanning
docker run --rm -v /home/samehabib/CMS-Platform:/app \
  aquasec/trivy image cms-platform-cms-backend:latest
```

### 2. Database Migration Strategy

```bash
# On production jposee-db:
# 1. Create backup
docker exec jposee-db pg_dump -U postgres jposee > /backup/jposee_pre_migration.sql

# 2. Run migration scripts (if any)
cat backend/migrations/001_create_jposee_schema.sql | \
  docker exec -i jposee-db psql -U postgres -d jposee

# 3. Verify schema
docker exec jposee-db psql -U postgres -d jposee -c "\dt"

# 4. Run data validation queries
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT COUNT(*) FROM jposee_transactions;"
```

### 3. Blue-Green Deployment

```bash
# Deploy to "Green" environment
docker compose -f docker-compose.green.yml up -d

# Run smoke tests against green environment
bash /tmp/test_jposee_apis.sh http://green-env:8000

# If tests pass, switch load balancer to green
# If tests fail, rollback to blue

# Update blue environment
docker compose -f docker-compose.blue.yml down
docker compose -f docker-compose.blue.yml up -d

# Perform health check
curl http://localhost:8000/jposee/monitoring/health
```

### 4. Canary Deployment (Progressive Rollout)

```bash
# Deploy to 10% of traffic
# Update load balancer weights:
#   - Old version: 90%
#   - New version: 10%

# Monitor metrics for 15 minutes
# If healthy, increase to 50%
# If metrics are good, increase to 100%
# If issues detected, rollback to old version
```

### 5. Rollback Procedure

```bash
# Immediate rollback
docker compose down
git checkout HEAD~1  # Revert to previous version
docker compose up -d

# Database rollback (if needed)
docker exec jposee-db psql -U postgres -d jposee -c \
  "ROLLBACK TRANSACTION;"

# Restore from backup if necessary
docker exec -i jposee-db psql -U postgres < /backup/jposee_pre_migration.sql

# Verify services
docker compose ps
curl http://localhost:8000/jposee/monitoring/health
```

## Production Hardening

### 1. Secret Management

```bash
# Use environment variable secrets file
# Store in secure location with restricted permissions
chmod 600 /etc/cms-platform/.env.production

# Or use dedicated secret management:
# - AWS Secrets Manager
# - HashiCorp Vault
# - Kubernetes Secrets
```

### 2. SSL/TLS Configuration

```bash
# Generate self-signed certificate (test only)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Use proper certificate (production)
# - Let's Encrypt via Certbot
# - AWS Certificate Manager
# - DigiCert/Verisign

# Configure in docker-compose.yml
volumes:
  - /etc/ssl/certs/cert.pem:/etc/ssl/certs/cert.pem:ro
  - /etc/ssl/private/key.pem:/etc/ssl/private/key.pem:ro
```

### 3. Rate Limiting Configuration

```python
# In backend/app/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/jposee/transactions")
@limiter.limit("100/minute")  # 100 requests per minute
async def list_transactions():
    ...
```

### 4. Audit Logging

```python
# Enable comprehensive logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "audit_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/cms-platform/audit.log",
            "maxBytes": 104857600,  # 100MB
            "backupCount": 10,
            "formatter": "detailed"
        }
    }
}
```

### 5. Database Security

```sql
-- Create read-only user for reporting
CREATE ROLE jposee_readonly LOGIN PASSWORD 'readonly_pass';
GRANT CONNECT ON DATABASE jposee TO jposee_readonly;
GRANT USAGE ON SCHEMA public TO jposee_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO jposee_readonly;

-- Create restricted user for API
CREATE ROLE jposee_api LOGIN PASSWORD 'api_pass';
GRANT CONNECT ON DATABASE jposee TO jposee_api;
GRANT USAGE ON SCHEMA public TO jposee_api;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO jposee_api;

-- Enable SSL
alter system set ssl = on;
```

## Monitoring & Alerting

### Key Metrics to Monitor

```yaml
Application Metrics:
  - Request rate (requests/sec)
  - Response time (p50, p95, p99)
  - Error rate (4xx, 5xx per minute)
  - Transaction throughput
  - API endpoint latency

Database Metrics:
  - Connection pool usage
  - Query execution time
  - Disk space usage
  - Replication lag (if applicable)
  - Lock contention

Infrastructure Metrics:
  - CPU utilization
  - Memory usage
  - Disk I/O
  - Network bandwidth
  - Container restart count
```

### Prometheus Scrape Config

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'jposee-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']  # postgres_exporter

  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9323']  # docker stats
```

### Alert Rules

```yaml
groups:
  - name: cms-platform
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: LowDiskSpace
        expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1
        for: 10m
        annotations:
          summary: "Disk space below 10%"

      - alert: DatabaseConnectionPool
        expr: pg_stat_activity_count > 90
        for: 5m
        annotations:
          summary: "Database connection pool near limit"
```

## Backup & Disaster Recovery

### Automated Backup Schedule

```bash
#!/bin/bash
# /usr/local/bin/backup-jposee.sh

BACKUP_DIR="/backups/jposee"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="jposee"

# Daily backup at 2 AM
docker exec jposee-db pg_dump -U postgres ${DB_NAME} | \
  gzip > ${BACKUP_DIR}/${DB_NAME}_${DATE}.sql.gz

# Keep only 30 days of backups
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +30 -delete

# Weekly backup to S3 (recommended)
aws s3 cp ${BACKUP_DIR}/${DB_NAME}_${DATE}.sql.gz \
  s3://backup-bucket/jposee/
```

### Recovery Point Objectives (RPO/RTO)

| Tier | RTO | RPO | Strategy |
|------|-----|-----|----------|
| Gold | 1 hour | 15 min | Hot standby + real-time sync |
| Silver | 4 hours | 1 hour | Daily incremental backups |
| Bronze | 24 hours | 1 day | Daily full backups |

## Performance Optimization

### Docker Resource Limits

```yaml
services:
  cms-backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Database Connection Pool Tuning

```python
# In backend/app/database/jposee.py
pool = psycopg2.pool.SimpleConnectionPool(
    minconn=5,      # Start with 5 connections
    maxconn=20,     # Max 20 connections
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    database=settings.POSTGRES_DB,
    connect_timeout=5
)
```

### Caching Strategy

```python
# Redis caching for frequently accessed data
from functools import lru_cache
from redis import Redis

redis_client = Redis(host='redis-cache', port=6379, db=0)

@app.get("/jposee/transactions")
@lru_cache(maxsize=128)
async def list_transactions(page: int = 1, limit: int = 10):
    cache_key = f"transactions:{page}:{limit}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    # ... fetch from DB
    # redis_client.setex(cache_key, 3600, json.dumps(result))
```

## Maintenance Windows

### Planned Maintenance Schedule

- **Primary maintenance window**: Sundays 02:00-04:00 UTC
- **Hotfix window**: Weekdays 01:00-02:00 UTC (as needed)
- **Security patches**: Within 24 hours of release

### Maintenance Procedures

```bash
# Announce maintenance window (at least 24h before)
# Drain connections gracefully
docker compose exec cms-backend graceful-shutdown

# Update images
docker compose pull

# Run database migrations
docker compose exec jposee-db psql -U postgres -d jposee < migrations/002_*.sql

# Restart services
docker compose restart

# Run health checks
bash /tmp/test_jposee_apis.sh

# Restore services to normal
# Announce maintenance complete
```

## Post-Deployment Validation

```bash
# 1. Health check
curl -I https://api.cms-platform.com/jposee/monitoring/health

# 2. Database connectivity
curl https://api.cms-platform.com/jposee/transactions

# 3. Create test transaction
curl -X POST https://api.cms-platform.com/jposee/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "txn_id": "PROD-TEST-001",
    "amount": 100.00,
    "currency": "USD",
    "txn_type": "Purchase"
  }'

# 4. Verify routing
curl -X POST https://api.cms-platform.com/jposee/routing/test \
  -d '{"amount": 500.00}'

# 5. Check logs
docker compose logs -f cms-backend --tail=100

# 6. Monitor metrics
# Check Prometheus at https://metrics.cms-platform.com
# Check Grafana dashboards
```

## Compliance & Security

### GDPR Compliance

- [ ] Data encryption at rest
- [ ] Data encryption in transit (TLS)
- [ ] Right to be forgotten implemented
- [ ] Data retention policies configured
- [ ] Privacy policy available

### PCI DSS Compliance (for payment processing)

- [ ] No storage of card details
- [ ] TLS 1.2 or higher
- [ ] Strong authentication
- [ ] Regular security audits
- [ ] Tokenization of payment data

### SOC 2 Compliance

- [ ] Audit logging enabled
- [ ] Change management process
- [ ] Incident response plan
- [ ] Access controls enforced
- [ ] Encryption standards met

## Troubleshooting Production Issues

### High Memory Usage

```bash
# Identify memory leaks
docker stats cms-backend --no-stream

# Check Python memory profile
docker exec cms-backend python -m memory_profiler

# Restart if necessary
docker compose restart cms-backend
```

### Slow Queries

```bash
# Enable query logging
docker exec jposee-db psql -U postgres -d jposee -c \
  "ALTER DATABASE jposee SET log_statement = 'all';"

# Find slow queries
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT query, calls, mean_time FROM pg_stat_statements \
   ORDER BY mean_time DESC LIMIT 10;"
```

### Connection Pool Exhaustion

```bash
# Check active connections
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT COUNT(*) FROM pg_stat_activity;"

# Kill idle connections
docker exec jposee-db psql -U postgres -d jposee -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity \
   WHERE state = 'idle' AND query_start < now() - interval '30 minutes';"
```

## Support & Escalation

### Support Channels
- **Critical (P1)**: Page on-call engineer via PagerDuty
- **High (P2)**: Email: ops-team@cms-platform.com
- **Medium (P3)**: Slack: #ops-support
- **Low (P4)**: Jira ticket

### Escalation Matrix
- L1: DevOps team (4 hours)
- L2: Platform engineering (2 hours)
- L3: CTO (1 hour)

---

**Last Updated**: April 21, 2026  
**Platform Version**: 1.0.0  
**Contact**: ops-team@cms-platform.com
