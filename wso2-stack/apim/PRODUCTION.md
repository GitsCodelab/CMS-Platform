# WSO2 API Manager - Production Configuration

This file contains production-ready configurations for WSO2 API Manager.

## SSL/TLS Certificate Setup

### Using Self-Signed Certificates (Development)

Already included in WSO2 default installation.

### Using CA-Signed Certificates (Production)

1. **Place certificate in Docker volume**:
```bash
cp /path/to/certificate.p12 wso2am-data/
cp /path/to/private-key.key wso2am-data/
```

2. **Update docker-compose.yml**:
```yaml
environment:
  KEYSTORE_FILE: /home/wso2carbon/wso2am-4.1.0/repository/resources/security/certificate.p12
  KEYSTORE_PASSWORD: your_keystore_password
  KEY_PASSWORD: your_key_password
```

3. **Restart service**:
```bash
docker compose restart cms-apim
```

## Database Configuration for Production

### PostgreSQL Connection Pooling

```yaml
environment:
  DB_JDBC_POOL_SIZE: 50
  DB_JDBC_MAX_IDLE_CONNECTIONS: 10
  DB_JDBC_CONNECTION_TIMEOUT: 30000
  DB_JDBC_VALIDATION_QUERY: "SELECT 1"
```

### Enable Database Backups

```bash
# Daily backup script
#!/bin/bash
docker exec cms-postgresql pg_dump -U postgres wso2am \
  | gzip > backup-$(date +%Y-%m-%d).sql.gz
```

### High Availability Setup (Optional)

```yaml
# Use external PostgreSQL cluster
environment:
  DB_HOSTNAME: postgresql-master.example.com
  DB_PORT: 5432
  DB_REPLICAS: postgresql-replica.example.com:5432
```

## Security Configuration

### 1. Change Default Credentials

```bash
# In Publisher, go to Settings → Users Management
# Change admin password immediately
```

### 2. Enable API Key Validation

```yaml
environment:
  API_KEY_VALIDATION: true
  API_KEY_HEADER: X-API-Key
```

### 3. Configure OAuth2 Token Expiration

```yaml
environment:
  OAUTH2_TOKEN_EXPIRY: 3600        # 1 hour
  OAUTH2_REFRESH_TOKEN_EXPIRY: 86400  # 24 hours
```

### 4. Enable HTTPS Enforcement

```yaml
environment:
  ENFORCE_HTTPS: true
  HTTP_TO_HTTPS_REDIRECT: true
```

## Performance Tuning

### Memory Configuration

```yaml
environment:
  JAVA_OPTS: |
    -Xms2g
    -Xmx4g
    -XX:+UseG1GC
    -XX:MaxGCPauseMillis=200
```

### Connection Pool Optimization

```yaml
environment:
  DB_JDBC_POOL_SIZE: 100
  DB_JDBC_MAX_IDLE_TIME: 600
  THREAD_POOL_SIZE: 200
```

### Cache Configuration

```yaml
environment:
  CACHE_ENABLED: true
  CACHE_MAX_SIZE: 10000
  CACHE_EXPIRY_TIME: 3600
```

## Monitoring & Logging

### 1. Enable Detailed Logging

```yaml
volumes:
  - wso2am-logs:/home/wso2carbon/wso2am-4.1.0/repository/logs
  
environment:
  LOG_LEVEL: DEBUG
  LOG_PATTERN: "%d [%t] %-5p %c{1} - %m%n"
```

### 2. Configure Log Rotation

```yaml
volumes:
  - ./log-rotation.xml:/home/wso2carbon/wso2am-4.1.0/repository/conf/log4j2.xml
```

### 3. Analytics/Monitoring Integration

```yaml
environment:
  ANALYTICS_ENABLED: true
  ANALYTICS_SERVER: https://analytics.example.com:7711
  ANALYTICS_SECRET: your_secret_key
```

### 4. Health Check Configuration

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "--retry", "3", 
         "https://localhost:9443/api/am/admin/v0.17/system-info", "-k"]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 180s  # Increased for production
```

## Rate Limiting (Throttling) Tiers

### Production Tier Configuration

```
GOLD Tier:
  - Requests/min: 10,000
  - Requests/day: 1,000,000
  - Cost: Premium

SILVER Tier:
  - Requests/min: 1,000
  - Requests/day: 100,000
  - Cost: Standard

BRONZE Tier:
  - Requests/min: 100
  - Requests/day: 10,000
  - Cost: Free/Trial
```

## Load Balancing Setup

### Nginx Reverse Proxy Configuration

```nginx
upstream apim_gateway {
    server cms-apim:8243 weight=1;
    server cms-apim2:8243 weight=1;
    server cms-apim3:8243 weight=1;
}

server {
    listen 8443 ssl;
    server_name api.example.com;

    ssl_certificate /etc/nginx/certs/cert.pem;
    ssl_certificate_key /etc/nginx/certs/key.pem;

    location / {
        proxy_pass https://apim_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Multi-Instance Deployment

```yaml
# docker-compose.yml
services:
  cms-apim:
    deploy:
      replicas: 3
    environment:
      CLUSTER_ENABLED: true
      CLUSTER_NODE_ID: apim-node-1
```

## Backup & Disaster Recovery

### Automated Backups

```bash
#!/bin/bash
# Daily backup of APIM configuration and data

BACKUP_DIR="/backup/wso2am"
DATE=$(date +%Y-%m-%d_%H-%M-%S)

# Backup PostgreSQL database
docker exec cms-postgresql pg_dump -U postgres wso2am | \
  gzip > $BACKUP_DIR/db-$DATE.sql.gz

# Backup APIM configuration
docker exec cms-apim tar czf - \
  /home/wso2carbon/wso2am-4.1.0/repository/conf | \
  > $BACKUP_DIR/config-$DATE.tar.gz

# Backup API definitions
docker exec cms-apim tar czf - \
  /home/wso2carbon/wso2am-4.1.0/repository/data | \
  > $BACKUP_DIR/data-$DATE.tar.gz

# Keep only last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

### Restore Procedure

```bash
# Restore database
gunzip -c /backup/wso2am/db-2024-01-15.sql.gz | \
  docker exec -i cms-postgresql psql -U postgres wso2am

# Restore configuration
docker exec cms-apim tar xzf - \
  -C /home/wso2carbon/wso2am-4.1.0/ < \
  /backup/wso2am/config-2024-01-15.tar.gz

# Restart service
docker compose restart cms-apim
```

## GDPR & Data Privacy

### Data Retention Policies

```yaml
environment:
  LOG_RETENTION_DAYS: 90
  ANALYTICS_RETENTION_DAYS: 365
  AUDIT_LOG_RETENTION_DAYS: 730
```

### Sensitive Data Masking

```yaml
environment:
  MASK_SENSITIVE_DATA: true
  MASKED_HEADERS: "Authorization,X-API-Key,Password"
  MASKED_FIELDS: "password,secret,token,credit_card"
```

## Compliance & Auditing

### API Usage Audit Trail

```yaml
environment:
  AUDIT_LOGGING: true
  AUDIT_EVENTS:
    - API_CREATE
    - API_UPDATE
    - API_DELETE
    - API_PUBLISH
    - USER_LOGIN
    - USER_LOGOUT
```

### Compliance Reporting

Configure automated reports:
- Daily API usage summary
- Weekly security audit
- Monthly compliance report

## Production Deployment Checklist

- [ ] SSL/TLS certificates installed (not self-signed)
- [ ] Database backups configured
- [ ] Admin credentials changed
- [ ] High memory allocation (2GB+)
- [ ] Connection pooling enabled
- [ ] Logging configured and rotated
- [ ] Rate limiting tiers configured
- [ ] Health checks passing
- [ ] Load balancer configured
- [ ] Monitoring & alerting setup
- [ ] Disaster recovery plan documented
- [ ] Security audit completed
- [ ] Performance benchmarked
- [ ] Documentation updated

## Emergency Procedures

### Service Restart

```bash
docker compose restart cms-apim
```

### Full Service Reset (Caution!)

```bash
# Stop and remove containers
docker compose down cms-apim

# Remove volumes (WARNING: deletes data!)
docker volume rm wso2am-data wso2am-logs

# Restart
docker compose up -d cms-apim
```

### Database Emergency Restore

```bash
# Restore from backup
gunzip -c /backup/wso2am/db-latest.sql.gz | \
  docker exec -i cms-postgresql psql -U postgres wso2am

# Verify
docker exec cms-postgresql psql -U postgres -d wso2am -c "SELECT COUNT(*) FROM AM_API;"
```

## Support & Escalation

- **Technical Support**: support@wso2.com
- **Issue Tracking**: GitHub Issues
- **Community Forum**: StackOverflow (tag: wso2-apim)
- **Emergency Hotline**: Available for enterprise customers

## References

- [WSO2 APIM Production Deployment Guide](https://apim.docs.wso2.com/en/4.1.0/setup/production-deployment/)
- [Performance Tuning](https://apim.docs.wso2.com/en/4.1.0/setup/performance-tuning/)
- [Security Hardening](https://apim.docs.wso2.com/en/4.1.0/setup/security/)
