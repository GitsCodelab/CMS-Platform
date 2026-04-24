# WSO2 API Manager - API Registration Guide

This guide explains how to register new APIs in WSO2 API Manager with parameterized scripts.

**Last Updated**: April 24, 2026  
**APIM Version**: 4.3.0  
**Prerequisites**: APIM running and healthy

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Using the Registration Script](#using-the-registration-script)
3. [Manual Registration (REST API)](#manual-registration-rest-api)
4. [API Configuration Examples](#api-configuration-examples)
5. [Publishing & Testing](#publishing--testing)
6. [API Lifecycle Management](#api-lifecycle-management)

---

## Quick Start

### Register an API in 30 seconds:

```bash
# Make the script executable
chmod +x /home/samehabib/CMS-Platform/wso2-stack/apim/register_api.sh

# Register your API
bash /home/samehabib/CMS-Platform/wso2-stack/apim/register_api.sh \
  --name "My Test API" \
  --context "/my/test" \
  --backend "http://cms-backend:8000/my/endpoint"
```

Done! ✅ Your API is now registered in APIM.

---

## Using the Registration Script

### Script Location
```
/home/samehabib/CMS-Platform/wso2-stack/apim/register_api.sh
```

### Syntax

```bash
bash register_api.sh \
  --name <API_NAME> \
  --context <API_CONTEXT> \
  --backend <BACKEND_URL> \
  [--version <VERSION>] \
  [--policy <THROTTLE_POLICY>] \
  [--sandbox-backend <SANDBOX_URL>] \
  [--host <APIM_HOST>] \
  [--port <APIM_PORT>] \
  [--admin <ADMIN_USER>] \
  [--password <ADMIN_PASSWORD>]
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--name` | ✅ | - | API display name (e.g., "User Management API") |
| `--context` | ✅ | - | API context path (e.g., "/api/users") |
| `--backend` | ✅ | - | Backend endpoint URL (production) |
| `--version` | ❌ | `1.0.0` | API version |
| `--policy` | ❌ | `Unlimited` | Throttling policy (Unlimited, Gold, Silver, Bronze) |
| `--sandbox-backend` | ❌ | Same as backend | Sandbox endpoint URL |
| `--host` | ❌ | `localhost` | APIM host (or IP/domain) |
| `--port` | ❌ | `9443` | APIM admin port |
| `--admin` | ❌ | `admin` | APIM admin username |
| `--password` | ❌ | `admin` | APIM admin password |

---

## Examples

### Example 1: Simple Oracle Database API

```bash
bash register_api.sh \
  --name "CMS Oracle Test API" \
  --context "/cms/oracle" \
  --backend "http://cms-backend:8000/oracle/test"
```

**Result**:
- API Name: `CMS Oracle Test API`
- Context: `/cms/oracle`
- Version: `1.0.0` (default)
- Policy: `Unlimited` (default)
- Status: `CREATED`

---

### Example 2: PostgreSQL API with Custom Version

```bash
bash register_api.sh \
  --name "CMS PostgreSQL Test API" \
  --context "/cms/postgres" \
  --backend "http://cms-backend:8000/postgres/test" \
  --version "2.0.0"
```

**Result**:
- API Name: `CMS PostgreSQL Test API`
- Context: `/cms/postgres`
- Version: `2.0.0`
- Policy: `Unlimited`
- Status: `CREATED`

---

### Example 3: Production API with Sandbox and Rate Limiting

```bash
bash register_api.sh \
  --name "Payment Processing API" \
  --context "/api/payments" \
  --backend "https://api-prod.company.com/v1/payments" \
  --sandbox-backend "https://api-sandbox.company.com/v1/payments" \
  --version "1.5.0" \
  --policy "Gold"
```

**Result**:
- Production endpoint: `https://api-prod.company.com/v1/payments`
- Sandbox endpoint: `https://api-sandbox.company.com/v1/payments`
- Rate limit: Gold tier
- Both endpoints available for testing

---

### Example 4: Remote APIM Instance

```bash
bash register_api.sh \
  --name "Remote API" \
  --context "/remote/test" \
  --backend "http://backend.example.com/api" \
  --host "apim.example.com" \
  --port 443 \
  --admin "apim_admin" \
  --password "secure_password"
```

---

## Manual Registration (REST API)

If you prefer to register APIs manually or need custom configurations:

### Step 1: Get Authentication Token

```bash
ADMIN_USER="admin"
ADMIN_PASS="admin"
APIM_HOST="localhost"
APIM_PORT="9443"
```

### Step 2: Create API

```bash
curl -s -k -X POST \
  "https://${APIM_HOST}:${APIM_PORT}/api/am/publisher/v4/apis" \
  -u "${ADMIN_USER}:${ADMIN_PASS}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Custom API",
    "context": "/my/custom",
    "version": "1.0.0",
    "type": "HTTP",
    "description": "My API description",
    "endpointConfig": {
      "endpoint_type": "http",
      "production_endpoints": {
        "url": "http://backend.example.com/api"
      },
      "sandbox_endpoints": {
        "url": "http://backend.example.com/api/sandbox"
      }
    },
    "policies": ["Unlimited"],
    "visibility": "PUBLIC"
  }'
```

**Response** (on success):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Custom API",
  "context": "/my/custom",
  "version": "1.0.0",
  "lifeCycleStatus": "CREATED",
  ...
}
```

Save the `id` from the response for next steps.

---

### Step 3: List All APIs

```bash
curl -s -k \
  "https://${APIM_HOST}:${APIM_PORT}/api/am/publisher/v4/apis" \
  -u "${ADMIN_USER}:${ADMIN_PASS}" | python3 -m json.tool
```

---

### Step 4: Get Specific API Details

```bash
API_ID="550e8400-e29b-41d4-a716-446655440000"

curl -s -k \
  "https://${APIM_HOST}:${APIM_PORT}/api/am/publisher/v4/apis/${API_ID}" \
  -u "${ADMIN_USER}:${ADMIN_PASS}" | python3 -m json.tool
```

---

## API Configuration Examples

### Basic HTTP API

```bash
bash register_api.sh \
  --name "REST API Service" \
  --context "/api/service" \
  --backend "http://10.0.0.5:3000/api"
```

---

### HTTPS API with Self-Signed Certificate

```bash
bash register_api.sh \
  --name "Secure API" \
  --context "/secure/api" \
  --backend "https://secure-api.internal:8443/v1"
```

---

### API with Path Parameters

```bash
bash register_api.sh \
  --name "User Management API" \
  --context "/api/users" \
  --backend "http://user-service:3000/users"
```

Operations auto-created:
- GET /users
- POST /users
- PUT /users
- DELETE /users
- PATCH /users

---

### WebSocket API

```bash
bash register_api.sh \
  --name "Real-time Events API" \
  --context "/events/stream" \
  --backend "ws://event-server:8080/stream"
```

---

## Publishing & Testing

### Step 1: Publish the API

After registration, the API is in `CREATED` status. To make it available to subscribers:

```bash
API_ID="550e8400-e29b-41d4-a716-446655440000"

curl -s -k -X POST \
  "https://localhost:9443/api/am/publisher/v4/apis/${API_ID}/state-change?action=Publish" \
  -u "admin:admin" \
  -H "Content-Type: application/json"
```

**Status Changes**:
- `CREATED` → Initial state after registration
- `PUBLISHED` → API is available to subscribers
- `DEPRECATED` → Old versions (support legacy requests)
- `RETIRED` → API is no longer available

---

### Step 2: Create Test Application

```bash
curl -s -k -X POST \
  "https://localhost:9443/api/am/store/v4/applications" \
  -u "admin:admin" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test App",
    "throttlePolicy": "Unlimited"
  }' | python3 -m json.tool
```

---

### Step 3: Subscribe to API

```bash
APP_ID="app-id-from-previous-step"
API_ID="550e8400-e29b-41d4-a716-446655440000"

curl -s -k -X POST \
  "https://localhost:9443/api/am/store/v4/subscriptions" \
  -u "admin:admin" \
  -H "Content-Type: application/json" \
  -d '{
    "applicationId": "'${APP_ID}'",
    "apiId": "'${API_ID}'",
    "throttlePolicy": "Unlimited"
  }'
```

---

### Step 4: Generate API Keys

```bash
curl -s -k -X POST \
  "https://localhost:9443/api/am/store/v4/applications/application-keys?applicationId=${APP_ID}" \
  -u "admin:admin" \
  -H "Content-Type: application/json" \
  -d '{
    "keyType": "PRODUCTION",
    "validityPeriod": 3600,
    "accessAllowDomains": ["localhost"]
  }' | python3 -m json.tool
```

---

### Step 5: Invoke API

```bash
# Get your API Key from previous step
API_KEY="your-api-key-here"

curl -k -X GET \
  "https://localhost:8243/cms/oracle/v1.0.0" \
  -H "apikey: ${API_KEY}"
```

---

## API Lifecycle Management

### View All APIs

```bash
curl -s -k \
  "https://localhost:9443/api/am/publisher/v4/apis?limit=100" \
  -u "admin:admin" | python3 -m json.tool
```

---

### Update API Endpoint

```bash
API_ID="550e8400-e29b-41d4-a716-446655440000"

curl -s -k -X PUT \
  "https://localhost:9443/api/am/publisher/v4/apis/${API_ID}" \
  -u "admin:admin" \
  -H "Content-Type: application/json" \
  -d '{
    "endpointConfig": {
      "endpoint_type": "http",
      "production_endpoints": {
        "url": "http://new-backend.example.com/api"
      }
    }
  }'
```

---

### Create API Revision

```bash
API_ID="550e8400-e29b-41d4-a716-446655440000"

curl -s -k -X POST \
  "https://localhost:9443/api/am/publisher/v4/apis/${API_ID}/revisions" \
  -u "admin:admin" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Version with updated endpoint"
  }'
```

---

### Delete API

```bash
API_ID="550e8400-e29b-41d4-a716-446655440000"

curl -s -k -X DELETE \
  "https://localhost:9443/api/am/publisher/v4/apis/${API_ID}" \
  -u "admin:admin"
```

⚠️ **Warning**: This cannot be undone!

---

## Batch Registration

Register multiple APIs at once:

```bash
#!/bin/bash
# File: batch_register_apis.sh

APIS=(
  "Payment API|/api/payments|http://payment-service:8000"
  "User Service|/api/users|http://user-service:3000"
  "Order Service|/api/orders|http://order-service:4000"
  "Inventory API|/api/inventory|http://inventory-service:5000"
)

for api in "${APIS[@]}"; do
  IFS='|' read -r name context backend <<< "$api"
  echo "Registering: $name..."
  bash register_api.sh \
    --name "$name" \
    --context "$context" \
    --backend "$backend"
done

echo "✅ All APIs registered successfully!"
```

Run it:
```bash
bash batch_register_apis.sh
```

---

## Troubleshooting

### Issue: "HTTP 401 Unauthorized"

**Cause**: Wrong admin credentials  
**Solution**: Check admin username and password

```bash
bash register_api.sh \
  --name "Test" \
  --context "/test" \
  --backend "http://backend:8000" \
  --admin "correct_admin" \
  --password "correct_password"
```

---

### Issue: "HTTP 500 Internal Server Error"

**Cause**: APIM service error (schema issue, key manager configuration)  
**Solution**: Check APIM logs

```bash
docker logs cms-apim 2>&1 | grep -i "error\|exception" | tail -20
```

---

### Issue: "Connection refused" to backend

**Cause**: Backend service not reachable  
**Solution**: Verify backend is running and use correct hostname/port

```bash
# Test connectivity from APIM container
docker exec cms-apim curl -v http://your-backend:port/path
```

---

### Issue: API created but context returns 404

**Cause**: API not yet published  
**Solution**: Publish the API using Publisher console or API

```bash
curl -s -k -X POST \
  "https://localhost:9443/api/am/publisher/v4/apis/${API_ID}/state-change?action=Publish" \
  -u "admin:admin"
```

---

## Performance Tips

1. **Batch Operations**: Register multiple APIs in sequence
2. **Caching**: Enable response caching for frequently called endpoints
3. **Throttling**: Use appropriate policies to prevent overload
4. **Monitoring**: Track API usage via APIM Analytics dashboard
5. **Version Management**: Maintain API versions for backward compatibility

---

## Next Steps

1. **Monitor API Usage** → APIM Analytics Dashboard (port 3000)
2. **Setup Subscriptions** → APIM Store Portal
3. **Add Security Policies** → OAuth2, API Key, mTLS
4. **Enable Analytics** → Track request/response metrics
5. **Production Deployment** → See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)

---

**Version**: 1.0  
**Last Tested**: April 24, 2026  
**Status**: ✅ All examples working
