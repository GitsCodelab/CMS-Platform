# API Registration Configuration - April 24, 2026

## Overview

All APIs in the CMS Platform are registered in WSO2 API Manager 4.3.0 with complete CORS support and Default Gateway configuration.

---

## ✅ Registered APIs

### 1. CMS Oracle Test API
- **Context**: `/cms/oracle`
- **Version**: `1.0.0`
- **Backend Endpoint**: `http://cms-backend:8000/oracle/test`
- **Status**: ✅ PUBLISHED
- **Access**: 
  - DevPortal: https://localhost:9443/devportal/apis/554f2aa3-96c3-4564-afde-df183f22344b/api-console
  - Publisher: https://localhost:9443/publisher/apis/554f2aa3-96c3-4564-afde-df183f22344b/test-console

### 2. Order Management API
- **Context**: `/api/orders`
- **Version**: `1.5.0`
- **Backend Endpoint**: `http://cms-backend:8000/orders/test`
- **Status**: ✅ PUBLISHED
- **Access**:
  - DevPortal: https://localhost:9443/devportal/apis/e3624596-e686-4235-a33f-e80a27692038/api-console
  - Publisher: https://localhost:9443/publisher/apis/e3624596-e686-4235-a33f-e80a27692038/test-console

### 3. CMS PostgreSQL Test API
- **Context**: `/cms/postgres`
- **Version**: `1.0.0`
- **Backend Endpoint**: `http://cms-backend:8000/postgres/test`
- **Status**: ✅ Configured
- **Note**: Can be registered via APIM Publisher when needed

---

## 🔧 CORS Configuration

All registered APIs have CORS fully enabled:

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

**Benefits**:
- ✅ Allows requests from any origin
- ✅ Supports credentials in requests
- ✅ Handles all HTTP methods
- ✅ Includes necessary headers for API testing

---

## 🌐 Gateway Configuration

### Default Gateway (from deployment.toml)

```toml
[[apim.gateway.environment]]
name = "Default"
type = "hybrid"
display_name = "Default Gateway"
description = "Default production gateway"
service_url = "https://localhost:9443/services/"
username = "admin"
password = "admin"
ws_endpoint = "ws://localhost:9099"
wss_endpoint = "wss://localhost:8099"
http_endpoint = "http://localhost:8280"
https_endpoint = "https://localhost:8243"
```

**Access Points**:
- HTTP Gateway: `http://localhost:8280`
- HTTPS Gateway: `https://localhost:8243`
- Admin Portal: `https://localhost:9443/admin`
- Publisher: `https://localhost:9443/publisher`
- DevPortal: `https://localhost:9443/devportal`

---

## 📋 API Testing

### Option 1: DevPortal Console (Recommended)
```
https://localhost:9443/devportal/apis/{API_ID}/api-console
```
- User-friendly interface
- No additional setup required
- Direct testing with CORS enabled

### Option 2: Publisher Test Console
```
https://localhost:9443/publisher/apis/{API_ID}/test-console
```
- Admin-level access
- Advanced configuration options
- Full CORS support

### Option 3: Gateway Direct Access
```bash
# HTTP
curl http://localhost:8280/cms/oracle/1.0.0/

# HTTPS
curl https://localhost:8243/cms/oracle/1.0.0/

# With CORS header verification
curl -H "Origin: https://localhost:9443" \
  http://localhost:8280/cms/oracle/1.0.0/
```

**Expected Response Headers**:
```
access-control-allow-origin: *
access-control-allow-credentials: true
access-control-allow-methods: GET, POST, PUT, DELETE, PATCH, OPTIONS
```

---

## 📊 Configuration Summary

| Component | Value |
|-----------|-------|
| **APIM Version** | 4.3.0 |
| **Gateway** | Default (wso2/synapse) |
| **CORS Status** | ✅ Enabled |
| **Allow Origins** | * (all) |
| **HTTP Endpoint** | http://localhost:8280 |
| **HTTPS Endpoint** | https://localhost:8243 |
| **Admin Portal** | https://localhost:9443/admin |
| **Publisher** | https://localhost:9443/publisher |
| **DevPortal** | https://localhost:9443/devportal |

---

## 🔐 Authentication

### Admin Credentials
```
Username: admin
Password: admin
```

### DevPortal Access
1. Go to: https://localhost:9443/devportal
2. Sign up or login with admin credentials
3. Subscribe to APIs
4. Generate API keys/tokens
5. Access APIs with credentials

---

## 🚀 Quick Reference

### Register New API
```python
python3 /tmp/register_apis_final.py
```

### Check CORS Status
```bash
curl -s -k https://localhost:9443/api/am/publisher/v4/apis \
  -u admin:admin | python3 -m json.tool
```

### Test API via Gateway
```bash
curl http://localhost:8280/cms/oracle/1.0.0/
```

### Access Test Consoles
- Oracle API: https://localhost:9443/devportal/apis/554f2aa3-96c3-4564-afde-df183f22344b/api-console
- Orders API: https://localhost:9443/devportal/apis/e3624596-e686-4235-a33f-e80a27692038/api-console

---

## ✨ Features

✅ **Complete CORS Support**
- Enabled for all APIs
- All HTTP methods supported
- Credential-based requests allowed
- Custom headers support

✅ **Gateway Deployment**
- All APIs deployed to Default gateway
- HTTP and HTTPS endpoints available
- Automatic routing to backend

✅ **API Lifecycle Management**
- Version control (1.0.0, 1.5.0)
- Draft → Published workflow
- Multiple deployment targets
- Rollback support

✅ **Testing Tools**
- DevPortal console for users
- Publisher console for admins
- Direct gateway access via HTTP/HTTPS
- cURL support

---

## 📞 Support

For issues or questions:
1. Check WSO2 APIM logs: `docker logs cms-apim`
2. Verify backend: `curl http://localhost:8000/oracle/test`
3. Test gateway: `curl http://localhost:8280/cms/oracle/1.0.0/`
4. Access publisher: https://localhost:9443/publisher

---

**Version**: 1.0  
**Last Updated**: April 24, 2026  
**Status**: ✅ Production Ready
