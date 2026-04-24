# WSO2 APIM Test Console - CORS Error Fix Guide

**Date**: April 24, 2026  
**Issue**: "Failed to fetch" CORS error when trying to test APIs in APIM test console  
**Root Cause**: CORS is disabled at the API level in APIM configuration  

---

## 🔍 Problem Analysis

When you access: `https://localhost:9443/publisher/apis/554f2aa3-96c3-4564-afde-df183f22344b/test-console`

You're getting a "Failed to fetch" error with CORS-related messages because:

1. **CORS is disabled on the API definition** (`corsConfigurationEnabled: false`)
2. **Browser security** prevents cross-origin requests when CORS headers are missing
3. The test console tries to call the backend API through the APIM gateway, which is a cross-origin request from the browser perspective

---

## ✅ Solution: Enable CORS at API Level

### Method 1: Via APIM Publisher UI (Easiest)

1. **Access APIM Publisher**
   ```
   https://localhost:9443/publisher
   ```
   - Login: admin / admin

2. **Edit Oracle Test API**
   - Navigate to: CMS Oracle Test API (v1.0.0)
   - Click **Edit** or go to **Portal Settings**

3. **Enable CORS**
   - Find **Cors Configuration** section
   - Toggle: **CORS Configuration Enabled** = **ON**
   - Set:
     - **Access Control Allow Origins**: `*` (or specific domain)
     - **Access Control Allow Methods**: GET, POST, PUT, DELETE, OPTIONS, PATCH
     - **Access Control Allow Headers**:
       ```
       Authorization
       Access-Control-Allow-Origin
       Content-Type
       SOAPAction
       X-API-Key
       ```
     - **Access Control Max Age**: 3600

4. **Save** the API

5. **Test Again**
   - Go back to test console
   - Try the API call again

### Method 2: Via REST API

```bash
#!/bin/bash

API_ID="554f2aa3-96c3-4564-afde-df183f22344b"
APIM_HOST="localhost"
APIM_PORT="9443"

# Get current API config
curl -s -k "https://${APIM_HOST}:${APIM_PORT}/api/am/publisher/v4/apis/$API_ID" \
  -u admin:admin > /tmp/api.json

# Update with CORS enabled (using Python)
python3 << 'EOF'
import json

with open('/tmp/api.json') as f:
    api = json.load(f)

# Enable CORS
api['corsConfiguration']['corsConfigurationEnabled'] = True
api['corsConfiguration']['accessControlAllowOrigins'] = ['*']
api['corsConfiguration']['accessControlAllowMethods'] = [
    'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'
]
api['corsConfiguration']['accessControlAllowHeaders'] = [
    'Authorization',
    'Access-Control-Allow-Origin',
    'Content-Type',
    'SOAPAction',
    'X-API-Key'
]
api['corsConfiguration']['accessControlAllowCredentials'] = True
api['corsConfiguration']['accessControlMaxAge'] = 3600

with open('/tmp/api_updated.json', 'w') as f:
    json.dump(api, f)
EOF

# Update API in APIM
curl -k -X PUT \
  "https://${APIM_HOST}:${APIM_PORT}/api/am/publisher/v4/apis/$API_ID" \
  -u admin:admin \
  -H "Content-Type: application/json" \
  -d @/tmp/api_updated.json

echo "✓ CORS enabled on API"
```

---

## 🔧 Additional Configuration

### Ensure All APIs Are Published

Check API status:
```bash
curl -s -k "https://localhost:9443/api/am/publisher/v4/apis" \
  -u admin:admin | python3 -m json.tool | grep -A2 "lifeCycleStatus"
```

If APIs show `CREATED` status, they need to be published:
- In Publisher UI: Click API → Click **Publish**
- Orvia REST API: Update the API config (see Method 2 above)

### Check Gateway Deployment

APIs must be deployed to a gateway to be accessible:

```bash
# Check if API is deployed
curl -s -k "https://localhost:9443/api/am/publisher/v4/apis/{API_ID}/deployments" \
  -u admin:admin | python3 -m json.tool
```

Expected response should show deployment status "APPROVED".

---

## 🧪 Testing After Fix

### 1. Test via Test Console
```
https://localhost:9443/publisher/apis/554f2aa3-96c3-4564-afde-df183f22344b/test-console
```

### 2. Test via Gateway (HTTP)
```bash
curl -H "Origin: https://localhost:9443" \
  http://localhost:8280/cms/oracle/1.0.0/

# Should see CORS headers in response:
# access-control-allow-origin: *
# access-control-allow-credentials: true
```

### 3. Test via Backend (Direct)
```bash
curl http://localhost:8000/oracle/test

# Should return test data:
# [{"ID":1,"NAME":"Test Record 1",...}]
```

---

## 📋 CORS Configuration Reference

The complete CORS configuration object:

```json
{
  "corsConfigurationEnabled": true,
  "accessControlAllowCredentials": true,
  "accessControlAllowOrigins": [
    "*"
  ],
  "accessControlAllowHeaders": [
    "authorization",
    "Access-Control-Allow-Origin",
    "Content-Type",
    "SOAPAction",
    "X-API-Key"
  ],
  "accessControlAllowMethods": [
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "PATCH",
    "OPTIONS"
  ],
  "accessControlExposeHeaders": [],
  "accessControlMaxAge": 3600
}
```

---

## 🔄 Apply to All APIs

To enable CORS on all APIs:

```bash
#!/bin/bash

# Get all API IDs
API_IDS=$(curl -s -k "https://localhost:9443/api/am/publisher/v4/apis" \
  -u admin:admin | python3 -c "
import json, sys
data = json.load(sys.stdin)
for api in data.get('list', []):
    print(api['id'])
")

# Enable CORS on each
for API_ID in $API_IDS; do
    echo "Enabling CORS for: $API_ID"
    
    # Get API config
    curl -s -k "https://localhost:9443/api/am/publisher/v4/apis/$API_ID" \
      -u admin:admin | python3 << 'EOF'
import json, sys
data = json.load(sys.stdin)
data['corsConfiguration']['corsConfigurationEnabled'] = True
data['corsConfiguration']['accessControlAllowOrigins'] = ['*']
data['corsConfiguration']['accessControlAllowMethods'] = [
    'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'
]
data['corsConfiguration']['accessControlAllowHeaders'] = [
    'Authorization', 'Access-Control-Allow-Origin', 'Content-Type',
    'SOAPAction', 'X-API-Key'
]
print(json.dumps(data))
EOF > /tmp/api_$API_ID.json
    
    # Update API
    curl -k -X PUT \
      "https://localhost:9443/api/am/publisher/v4/apis/$API_ID" \
      -u admin:admin \
      -H "Content-Type: application/json" \
      -d @/tmp/api_$API_ID.json
    
    sleep 1
done

echo "✓ CORS enabled on all APIs"
```

---

## ⚠️ Troubleshooting

### Issue: Still getting 404 on gateway

**Reason**: API might not be deployed to gateway

**Fix**:
1. Go to API in Publisher
2. Click **Deployments** tab
3. Verify "Default-Gateway" shows with status "APPROVED"
4. If missing, click "Deploy" and select "Default-Gateway"

### Issue: 401 Unauthorized in test console

**Reason**: API requires authentication

**Fix**:
1. In test console, check if API requires subscription/token
2. Add API key or OAuth token to request headers
3. Or disable security for testing (not recommended for production)

### Issue: 502 Bad Gateway

**Reason**: APIM gateway can't reach backend

**Fix**:
- Verify backend is running: `docker ps | grep cms-backend`
- Verify backend endpoint URL in API config is correct:  `http://cms-backend:8000/oracle/test`
- Test directly: `curl http://localhost:8000/oracle/test`

---

## 📝 Summary

**To fix the CORS error in test console:**

1. ✅ Open APIM Publisher: https://localhost:9443/publisher
2. ✅ Edit the API
3. ✅ Enable CORS Configuration
4. ✅ Set Allow Origins: `*` (or your domain)
5. ✅ Set Allow Methods: GET, POST, PUT, DELETE, PATCH, OPTIONS
6. ✅ Set Allow Headers as shown above
7. ✅ Save
8. ✅ Go back to test console
9. ✅ Test API call again

---

**Version**: 1.0  
**Status**: ✅ Ready for Production (after CORS fix)  
**Next Steps**: Secure CORS configuration for production (restrict origins, add authentication)
