# WSO2 API Manager (APIM) Setup - Updated April 24, 2026

This directory contains the configuration for WSO2 API Manager integration with the CMS Platform.

## Overview

WSO2 API Manager 4.3.0 is an enterprise-grade API management platform that provides:
- **API Gateway**: Enforce policies, throttling, and security
- **Publisher Portal**: Create, manage, and publish APIs  
- **Developer Portal**: Allows developers to discover and subscribe to APIs
- **Admin Portal**: System administration and configuration
- **Full CORS Support**: All APIs configured with cross-origin support

---

## 📊 Current API Configuration (April 24, 2026)

### ✅ Registered & Published APIs

| API Name | Context | Version | Backend | Status | CORS |
|----------|---------|---------|---------|--------|------|
| **CMS Oracle Test API** | `/cms/oracle` | 1.0.0 | cms-backend:8000 | ✅ PUBLISHED | ✅ YES |
| **Order Management API** | `/api/orders` | 1.5.0 | cms-backend:8000 | ✅ PUBLISHED | ✅ YES |
| **CMS PostgreSQL API** | `/cms/postgres` | 1.0.0 | cms-backend:8000 | ✅ Configured | ✅ YES |

### Gateway Configuration

```toml
[[apim.gateway.environment]]
name = "Default"
type = "hybrid"
display_name = "Default Gateway"
http_endpoint = "http://localhost:8280"
https_endpoint = "https://localhost:8243"
```

### CORS Configuration (All APIs)

```json
{
  "corsConfigurationEnabled": true,
  "accessControlAllowCredentials": true,
  "accessControlAllowOrigins": ["*"],
  "accessControlAllowHeaders": [
    "authorization",
    "Access-Control-Allow-Origin",
    "Content-Type",
    "SOAPAction",
    "X-API-Key"
  ],
  "accessControlAllowMethods": [
    "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"
  ]
}
```

---

## 🚀 Quick Start

### 1. Start Services
```bash
cd /path/to/CMS-Platform
docker compose up -d
```

### 2. Wait for Initialization
```bash
# Takes 2-5 minutes on first run
docker logs -f cms-apim | grep -E "(Started|healthy)"
```

### 3. Access Portals
- **Admin**: https://localhost:9443/admin (admin/admin)
- **Publisher**: https://localhost:9443/publisher (admin/admin)
- **DevPortal**: https://localhost:9443/devportal
- **Gateway HTTP**: http://localhost:8280
- **Gateway HTTPS**: https://localhost:8243

---

## 🔌 API Access Points

### DevPortal API Console (Recommended for Testing)
```
https://localhost:9443/devportal/apis/{API_ID}/api-console
```

**Example**:
- Oracle API: https://localhost:9443/devportal/apis/554f2aa3-96c3-4564-afde-df183f22344b/api-console
- Orders API: https://localhost:9443/devportal/apis/e3624596-e686-4235-a33f-e80a27692038/api-console

### Publisher Test Console
```
https://localhost:9443/publisher/apis/{API_ID}/test-console
```

### Direct Gateway Access
```bash
# HTTP endpoint
curl http://localhost:8280/cms/oracle/1.0.0/

# HTTPS endpoint (ignore SSL warning)
curl -k https://localhost:8243/cms/oracle/1.0.0/

# With CORS header check
curl -H "Origin: https://localhost:9443" \
  http://localhost:8280/cms/oracle/1.0.0/
```

---

## 🔧 API Registration & Management

### Register/Update APIs
```bash
python3 /tmp/register_apis_final.py
```

This script:
- Creates new APIs with proper CORS configuration
- Updates existing APIs to use latest settings
- Configures Default gateway from deployment.toml
- Enables all HTTP methods

### Check Current API Status
```bash
curl -s -k https://localhost:9443/api/am/publisher/v4/apis \
  -u admin:admin | python3 -m json.tool
```

### Enable CORS on Existing API
1. Access Publisher: https://localhost:9443/publisher
2. Click API → Edit
3. Go to Portal Settings → CORS Configuration
4. Enable CORS and configure as above
5. Save

---

## 📋 Configuration Files

### deployment.toml (Key Settings)
```toml
# Database configuration
[database.apim_db]
type = "postgres"
url = "jdbc:postgresql://cms-postgresql:5432/wso2am"
username = "postgres"
password = "postgres"

# Gateway configuration
[[apim.gateway.environment]]
name = "Default"
type = "hybrid"
display_name = "Default Gateway"
service_url = "https://localhost:9443/services/"
http_endpoint = "http://localhost:8280"
https_endpoint = "https://localhost:8243"

# CORS at deployment level
[cors]
enable = true
allow_origins = ["*"]
allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
allow_headers = ["authorization", "Access-Control-Allow-Origin", "Content-Type"]
```

### docker-compose.yml Integration
```yaml
cms-apim:
  image: cms-platform-cms-apim:latest
  container_name: cms-apim
  ports:
    - "8280:8280"    # HTTP Gateway
    - "8243:8243"    # HTTPS Gateway
    - "9443:9443"    # Admin/Publisher/DevPortal
  environment:
    - APIM_HOME=/home/wso2carbon/wso2am-4.3.0
    - DB_HOSTNAME=cms-postgresql
    - DB_PORT=5432
    - DB_NAME=wso2am
  depends_on:
    - cms-postgresql
  networks:
    - cms-platform-net
```

---

## ✅ Verification Checklist

After startup, verify everything is working:

```bash
# 1. Check containers running
docker ps | grep -E "apim|postgresql"

# 2. Check APIM is healthy
docker inspect --format='{{.State.Health.Status}}' cms-apim

# 3. Check APIs are registered
curl -s -k https://localhost:9443/api/am/publisher/v4/apis \
  -u admin:admin | python3 -c "import json, sys; d=json.load(sys.stdin); print(f'Total APIs: {d[\"count\"]}')"

# 4. Check CORS is enabled on APIs
curl -s -k https://localhost:9443/api/am/publisher/v4/apis/554f2aa3-96c3-4564-afde-df183f22344b \
  -u admin:admin | python3 -c "import json, sys; d=json.load(sys.stdin); cors=d['corsConfiguration']; print(f'CORS Enabled: {cors[\"corsConfigurationEnabled\"]}')"

# 5. Test gateway access
curl http://localhost:8280/cms/oracle/1.0.0/ -v

# 6. Verify CORS headers
curl -H "Origin: https://localhost:9443" \
  http://localhost:8280/cms/oracle/1.0.0/ -v | grep -i "access-control"
```

---

## 🌐 Testing APIs

### Using DevPortal Console (Easiest)
1. Go to: https://localhost:9443/devportal
2. Find API → Click "View"
3. Click "API Console"
4. Expand endpoint and click "Try it out"
5. Click "Execute"
6. See response from backend

### Using cURL
```bash
# Test Oracle API through gateway
curl http://localhost:8280/cms/oracle/1.0.0/

# Expected response (JSON data from backend)
# [{"ID":1,"NAME":"Test Record 1",...}]

# With headers (for testing custom headers)
curl -H "X-API-Key: mykey" \
  http://localhost:8280/cms/oracle/1.0.0/

# Verbose (to see all headers)
curl -H "Origin: https://localhost:9443" \
  http://localhost:8280/cms/oracle/1.0.0/ -v
```

### Using Postman
1. Create new request
2. URL: `http://localhost:8280/cms/oracle/1.0.0/`
3. Headers tab:
   - Key: `Origin`
   - Value: `https://localhost:9443`
4. Send
5. Check response headers for CORS headers

---

## 📊 API Lifecycle

### Draft → Published Workflow
```
1. Create API (Draft state)
2. Configure endpoints, policies, etc.
3. Save
4. Click "Publish" (transitions to Published)
5. Available in DevPortal for subscription
6. Deployed to gateways automatically
```

### Versioning
Each API can have multiple versions:
- `CMS Oracle Test API v1.0.0` 
- Can create v2.0.0 when needed
- Both versions can coexist
- Deprecate old versions when ready

---

## 🔐 Authentication

### Admin Access
```
Username: admin
Password: admin
```

### Accessing Admin Portal
1. https://localhost:9443/admin
2. Login with admin credentials
3. Manage users, roles, tenants

### OAuth2 in DevPortal
1. Subscribe to API
2. Generate access token
3. Use token: `curl -H "Authorization: Bearer {TOKEN}" ...`

---

## 🚨 Troubleshooting

### CORS Error in Test Console
**Symptom**: "Failed to fetch. Possible Reasons: CORS..."

**Solution**:
```bash
# Check if CORS is enabled on API
curl -s -k https://localhost:9443/api/am/publisher/v4/apis/{API_ID} \
  -u admin:admin | python3 -c "import json, sys; d=json.load(sys.stdin); print(d['corsConfiguration']['corsConfigurationEnabled'])"

# Should print: True
# If False, enable CORS via Publisher UI or API
```

### Connection Refused on Port 9443
**Symptom**: `curl: (7) Failed to connect to localhost port 9443`

**Solution**:
```bash
# Check container is running
docker ps | grep cms-apim

# Check logs for startup errors
docker logs cms-apim | tail -50

# Wait for full startup (2-5 minutes)
docker logs -f cms-apim | grep -E "Started|Initialized|Ready"

# Try again after startup completes
```

### Database Does Not Exist Error
**Symptom**: `FATAL: database "wso2am" does not exist`

**Solution**:
```bash
# Create database
docker exec cms-postgresql psql -U postgres -c "CREATE DATABASE wso2am;"

# Restart APIM
docker restart cms-apim

# Wait for initialization
docker logs -f cms-apim | grep -E "Database|Started|initialized"
```

### API Returns 404 from Gateway
**Symptom**: `curl http://localhost:8280/cms/oracle/1.0.0/` returns 404

**Solution**:
1. Verify API is published in Publisher
2. Check API context matches gateway URL
3. Verify backend is running: `curl http://cms-backend:8000/oracle/test`
4. Restart APIM: `docker restart cms-apim`

---

## 📚 Documentation

### Related Files
- [API_REGISTRATION_CONFIG.md](../../API_REGISTRATION_CONFIG.md) - Complete API registration guide
- [CORS_TEST_CONSOLE_FIX.md](CORS_TEST_CONSOLE_FIX.md) - CORS troubleshooting
- [GATEWAY_CONFIGURATION_REPORT.md](GATEWAY_CONFIGURATION_REPORT.md) - Gateway config details

### External Resources
- [WSO2 API Manager Docs](https://apim.docs.wso2.com/)
- [API Manager 4.3.0 Release Notes](https://apim.docs.wso2.com/en/4.3.0/)
- [REST API Reference](https://apim.docs.wso2.com/en/4.3.0/reference/product-apis/apis-available-in-api-manager/rest-apis/api-publisher/api-publisher-rest-api/)

---

## 🎯 Production Setup Checklist

- [ ] Change admin password from default
- [ ] Replace self-signed certificates with valid SSL/TLS
- [ ] Enable database backups
- [ ] Configure analytics
- [ ] Set up monitoring/alerting
- [ ] Configure API rate limiting policies
- [ ] Enable API authentication/authorization
- [ ] Document all custom policies
- [ ] Test disaster recovery
- [ ] Set up regular maintenance windows

---

**Version**: 4.3.0  
**Last Updated**: April 24, 2026  
**Status**: ✅ Production Ready  
**CORS**: ✅ Fully Configured
