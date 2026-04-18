# WSO2 Identity Server Production Deployment Guide

This guide provides comprehensive instructions for deploying WSO2 Identity Server 7.0.0 in a production environment.

## Pre-Deployment Checklist

### Infrastructure Requirements

- [ ] Server with at least 8GB RAM, 4 CPU cores
- [ ] 50GB storage for database and logs
- [ ] Linux OS (CentOS, Ubuntu, or RHEL)
- [ ] Docker and Docker Compose installed
- [ ] PostgreSQL 12+ or Oracle 11g+ database
- [ ] SSL/TLS certificates (not self-signed)
- [ ] Load balancer (optional but recommended)
- [ ] Monitoring stack (Prometheus, Grafana)
- [ ] Log aggregation (ELK Stack)

### Network Security

- [ ] Configure firewall rules
- [ ] Enable VPN/SSH access
- [ ] Setup DDoS protection
- [ ] Configure WAF rules
- [ ] Enable rate limiting
- [ ] Setup network segmentation

### Data Protection

- [ ] Encryption at rest enabled
- [ ] Encryption in transit (TLS)
- [ ] Database backup strategy
- [ ] Disaster recovery plan
- [ ] Data retention policies

## Step 1: SSL/TLS Certificate Setup

### 1.1 Generate Self-Signed Certificate (Dev Only)

```bash
# Generate private key
openssl genrsa -out wso2is-key.pem 2048

# Generate CSR
openssl req -new -key wso2is-key.pem -out wso2is-csr.pem \
  -subj "/CN=cms-wso2is/O=CMS/C=US"

# Generate certificate
openssl x509 -req -days 365 -in wso2is-csr.pem \
  -signkey wso2is-key.pem -out wso2is-cert.pem

# Convert to PKCS12 (for Java keystore)
openssl pkcs12 -export -in wso2is-cert.pem -inkey wso2is-key.pem \
  -out wso2is.p12 -name wso2is -passout pass:wso2carbon
```

### 1.2 Import to Keystore

```bash
# Convert PKCS12 to JKS
keytool -importkeystore -srckeystore wso2is.p12 -srcstoretype PKCS12 \
  -srcstorepass wso2carbon -destkeystore wso2carbon.jks \
  -deststoretype JKS -deststorepass wso2carbon

# Copy to IS repository
docker compose exec cms-wso2is cp wso2carbon.jks \
  /home/wso2carbon/wso2is-7.0.0/repository/resources/security/
```

### 1.3 For Production - Use Proper Certificates

```bash
# Request certificate from CA
# Copy certificate and key to:
cp your-cert.pem /path/to/wso2-stack/wso2is/conf/
cp your-key.pem /path/to/wso2-stack/wso2is/conf/

# Update docker-compose.yml to mount certificates
volumes:
  - ./conf/your-cert.pem:/home/wso2carbon/wso2is-7.0.0/repository/resources/security/wso2carbon.jks
```

## Step 2: Database Configuration

### 2.1 Create Production Database

```sql
-- Connect to PostgreSQL
psql -U postgres -h localhost

-- Create database
CREATE DATABASE wso2is;

-- Create user with permissions
CREATE USER wso2is WITH PASSWORD 'SecurePassword123!';
ALTER ROLE wso2is WITH CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE wso2is TO wso2is;

-- Run schema scripts (provided by WSO2)
psql -U wso2is -d wso2is -f wso2is-schema.sql
```

### 2.2 Configure Connection Pooling

Update `.env`:
```env
# Database Connection Pooling
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

### 2.3 Enable Database SSL

```env
DB_SSL_ENABLED=true
DB_SSL_MODE=require
DB_SSL_CERT=/path/to/ca-cert.pem
```

## Step 3: Security Hardening

### 3.1 Change Default Passwords

```bash
# Update admin password
docker compose exec cms-wso2is bash
cd /home/wso2carbon/wso2is-7.0.0/bin

# Use admin console to change password
# Or use API:
curl -X POST https://localhost:9443/api/users/admin \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": "NewStrongPassword123!"}'
```

### 3.2 Disable Default Applications

```bash
# Access admin console
# Main → Applications → Remove default apps
```

### 3.3 Configure Authentication Policies

Edit deployment configuration:
```toml
[authentication.policy]
# Password policy
MIN_PASSWORD_LENGTH = 12
REQUIRE_UPPERCASE = true
REQUIRE_LOWERCASE = true
REQUIRE_NUMBERS = true
REQUIRE_SPECIAL_CHARS = true
PASSWORD_HISTORY_COUNT = 5

# Account lockout
ACCOUNT_LOCK_ENABLED = true
ACCOUNT_LOCK_THRESHOLD = 5
ACCOUNT_LOCK_TIME = 1800

# Session timeout
SESSION_TIMEOUT = 1800
```

### 3.4 Enable MFA for Admin

1. Access Admin Console: https://localhost:9443/carbon
2. Main → Users and Roles → Users
3. Select admin user
4. Enable two-factor authentication (TOTP)

### 3.5 Configure CORS

```toml
[cors]
enabled = true
allow_origins = ["https://localhost:3000", "https://api-gateway:8243"]
allow_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
allow_headers = ["Content-Type", "Authorization"]
max_age = 3600
```

## Step 4: Logging and Monitoring

### 4.1 Configure Logging

Create `conf/log4j2.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Configuration>
  <Appenders>
    <!-- File appender -->
    <File name="FileAppender" fileName="logs/wso2is.log">
      <PatternLayout pattern="%d{ISO8601} [%t] %-5p %c{1} - %m%n"/>
    </File>
    
    <!-- Async appender for performance -->
    <Async name="AsyncFileAppender" blocking="false">
      <AppenderRef ref="FileAppender"/>
    </Async>
    
    <!-- Audit log -->
    <File name="AuditLog" fileName="logs/audit.log">
      <PatternLayout pattern="%d{ISO8601} %m%n"/>
    </File>
  </Appenders>
  
  <Loggers>
    <Logger name="org.wso2.carbon" level="info" additivity="false">
      <AppenderRef ref="AsyncFileAppender"/>
    </Logger>
    
    <Logger name="org.wso2.carbon.user.core.authorization" level="debug" additivity="false">
      <AppenderRef ref="AuditLog"/>
    </Logger>
    
    <Root level="info">
      <AppenderRef ref="AsyncFileAppender"/>
    </Root>
  </Loggers>
</Configuration>
```

### 4.2 Enable Audit Logging

```toml
[audit_logging]
enabled = true
log_user_activities = true
log_authentication_attempts = true
log_permission_changes = true
retention_days = 365
```

### 4.3 Setup Monitoring

Install Prometheus endpoint exporter:

```bash
# Add to docker-compose.yml
environment:
  - ENABLE_METRICS=true
  - METRICS_PORT=9090

# Access metrics
curl http://localhost:9090/metrics
```

## Step 5: Backup and Recovery

### 5.1 Database Backup

```bash
#!/bin/bash
# backup-wso2is.sh

BACKUP_DIR="/backups/wso2is"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker compose exec -T cms-postgresql pg_dump -U wso2is wso2is | \
  gzip > $BACKUP_DIR/wso2is_db_$DATE.sql.gz

# Backup configuration
tar -czf $BACKUP_DIR/wso2is_config_$DATE.tar.gz \
  /path/to/wso2-stack/wso2is/conf

# Backup data directory
tar -czf $BACKUP_DIR/wso2is_data_$DATE.tar.gz \
  /path/to/wso2is-data-volume

# Remove old backups
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $DATE"
```

### 5.2 Restore from Backup

```bash
#!/bin/bash
# restore-wso2is.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file>"
  exit 1
fi

# Stop IS
docker compose down

# Restore database
gunzip < $BACKUP_FILE | docker compose exec -T cms-postgresql psql -U wso2is wso2is

# Restore configuration and data
tar -xzf $(dirname $BACKUP_FILE)/wso2is_config_*.tar.gz
tar -xzf $(dirname $BACKUP_FILE)/wso2is_data_*.tar.gz

# Start IS
docker compose up -d

echo "Restore completed from: $BACKUP_FILE"
```

## Step 6: Load Balancing

### 6.1 Configure with Nginx

```nginx
upstream wso2_is {
    server cms-wso2is:9443;
}

server {
    listen 443 ssl http2;
    server_name identity.example.com;

    ssl_certificate /etc/nginx/certs/cert.pem;
    ssl_certificate_key /etc/nginx/certs/key.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    location / {
        proxy_pass https://wso2_is;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

## Step 7: Performance Tuning

### 7.1 JVM Tuning

Update `.env`:
```env
JAVA_OPTS=
  -Xms2g -Xmx4g 
  -XX:+UseG1GC 
  -XX:MaxGCPauseMillis=20 
  -XX:InitiatingHeapOccupancyPercent=35 
  -XX:G1HeapRegionSize=16M 
  -XX:MinMetaspaceSize=256m 
  -XX:MaxMetaspaceSize=512m 
  -XX:+PrintGCDetails 
  -XX:+PrintGCDateStamps 
  -Xloggc:logs/gc.log
```

### 7.2 Database Connection Pool

```toml
[datasource]
max_pool_size = 50
min_idle = 10
max_idle = 30
connection_timeout = 30000
idle_timeout = 600000
max_lifetime = 1800000
```

### 7.3 Caching Configuration

```toml
[cache]
enabled = true
ttl = 900
max_entries = 10000
```

## Step 8: Monitoring and Alerting

### 8.1 Setup Health Checks

```bash
# Create monitoring script
#!/bin/bash

HEALTH_ENDPOINT="https://localhost:9443/api/identity/auth/v1.0/token"

curl -k -f $HEALTH_ENDPOINT
if [ $? -ne 0 ]; then
  echo "Health check failed at $(date)" | mail -s "WSO2 IS Down" ops@example.com
fi
```

### 8.2 Configure Alerts

Setup alerts for:
- Service down
- High CPU usage (>80%)
- High memory usage (>80%)
- Database connection errors
- Token generation failures
- Authentication failures (>100 in 5 min)

## Step 9: Disaster Recovery

### 9.1 RTO/RPO Definition

```
Recovery Time Objective (RTO): 1 hour
Recovery Point Objective (RPO): 15 minutes
```

### 9.2 Failover Configuration

```yaml
# docker-compose-ha.yml
version: '3.8'

services:
  wso2is-primary:
    image: wso2/wso2is:7.0.0
    environment:
      CLUSTER_ID: primary
  
  wso2is-secondary:
    image: wso2/wso2is:7.0.0
    environment:
      CLUSTER_ID: secondary
    depends_on:
      - wso2is-primary
```

## Production Deployment Checklist

- [ ] SSL/TLS certificates installed
- [ ] Database configured and tested
- [ ] Firewall rules implemented
- [ ] Admin passwords changed
- [ ] MFA enabled for admins
- [ ] Monitoring configured
- [ ] Logging configured
- [ ] Backup strategy implemented
- [ ] Load balancer configured
- [ ] JVM tuning applied
- [ ] Performance tests completed
- [ ] Disaster recovery plan tested
- [ ] Documentation completed
- [ ] Team trained on operations
- [ ] Incident response plan ready

## Useful Commands

```bash
# View logs
docker compose logs cms-wso2is -f

# SSH into container
docker compose exec cms-wso2is bash

# Restart service
docker compose restart cms-wso2is

# Check database
docker compose exec cms-postgresql psql -U wso2is -d wso2is -c "SELECT version();"

# Monitor resource usage
docker stats cms-wso2is

# Backup logs
tar -czf logs_backup_$(date +%s).tar.gz /path/to/wso2is/logs/
```

---

**Last Updated:** April 2026
**Version:** WSO2 IS 7.0.0
**Status:** Production Ready
**Maintainer:** DevOps Team
