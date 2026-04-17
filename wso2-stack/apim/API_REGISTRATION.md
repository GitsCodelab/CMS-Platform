# API Registration Guide for CMS Platform

This guide walks through registering the CMS Platform APIs in WSO2 API Manager.

## Quick Registration (Using Swagger/OpenAPI)

### Step 1: Access Publisher Portal

1. Open your browser: https://localhost:9443/publisher
2. Login with credentials:
   - Username: `admin`
   - Password: `admin`
3. Accept the self-signed SSL certificate (click "Advanced" → "Proceed")

### Step 2: Import API Definition

**Option A: From Swagger File**

1. Click **Create New API** → **Upload OpenAPI**
2. Select the file: `cms-api-definition.json` from this directory
3. Configure:
   - **API Name**: CMS Platform API
   - **API Version**: 1.0.0
   - **Context**: /cms
4. Click **Create & Publish**

**Option B: Manual REST API Creation**

1. Click **Create New API** → **Design a new REST API**
2. Fill in API Details:
   - **Name**: CMS Test API
   - **Context**: /cms/test
   - **Version**: 1.0.0
3. Click **Create**
4. Add Resources:
   - **Resource 1**:
     - **URL Pattern**: /oracle
     - **Methods**: GET, POST, PUT, DELETE
     - **Implementation**: http://cms-backend:8000/oracle
   - **Resource 2**:
     - **URL Pattern**: /postgres
     - **Methods**: GET, POST, PUT, DELETE
     - **Implementation**: http://cms-backend:8000/postgres

### Step 3: Configure API Endpoints

1. In the Publisher, go to **Endpoints** tab
2. Set production endpoint: `http://cms-backend:8000`
3. Set sandbox endpoint: `http://cms-backend:8000`
4. Click **Save**

### Step 4: Apply Policies

1. Go to **Policies** tab
2. Click **Add Policy** and select:
   - **CORS**: Enable CORS support
   - **Authentication**: OAuth2
   - **Throttling**: Gold tier (1000 req/min)
3. Save policies

### Step 5: Publish API

1. Click **Publish** button
2. API is now available in Developer Portal
3. Gateway endpoint: `https://localhost:8243/cms/test/1.0.0`

## Testing the API

### Using cURL

```bash
# 1. Generate OAuth2 Token
TOKEN=$(curl -X POST "https://localhost:9443/oauth2/token" \
  -H "Authorization: Basic YWRtaW46YWRtaW4=" \
  -d "grant_type=client_credentials" \
  -k -s | jq -r '.access_token')

# 2. Call API through Gateway
curl -X GET "https://localhost:8243/cms/test/1.0.0/oracle" \
  -H "Authorization: Bearer $TOKEN" \
  -k
```

### Using Postman

1. **Set up OAuth2 Collection**:
   - Authorization Type: OAuth2
   - Token URL: https://localhost:9443/oauth2/token
   - Client ID: (generated in APIM)
   - Client Secret: (generated in APIM)

2. **Create Request**:
   - Method: GET
   - URL: https://localhost:8243/cms/test/1.0.0/oracle
   - Headers: Authorization: Bearer {token}

3. **Send Request**

### Using Frontend Application

Update `frontend/src/api/client.js`:

```javascript
// Import axios
import axios from 'axios';

// Create API client pointing to APIM gateway
const apiClient = axios.create({
  baseURL: 'https://localhost:8243/cms/v1',
  timeout: 5000,
  httpsAgent: {
    rejectUnauthorized: false // For development only!
  }
});

// Add token injection interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired, redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

## API Subscription & Key Generation

### For Developers (using Developer Portal)

1. Access: https://localhost:9443/devportal
2. Login with credentials
3. Browse published APIs
4. Click **Subscribe** on desired API
5. Select application or create new one
6. Go to **Subscriptions** → View **Keys & Tokens**
7. Copy access token

### For Applications (programmatic)

```bash
# 1. Create OAuth2 Application
curl -X POST "https://localhost:9443/api/am/store/v1/applications" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "CMS App",
    "throttlePolicy": "Unlimited",
    "description": "CMS Platform Application"
  }' -k

# 2. Generate Keys
curl -X POST "https://localhost:9443/api/am/store/v1/applications/{app-id}/oauth-keys?keyType=PRODUCTION" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"validityTime": 3600}' -k

# 3. Use generated keys
TOKEN=$(curl -X POST "https://localhost:9443/oauth2/token" \
  -d "grant_type=client_credentials" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" -k -s | jq -r '.access_token')
```

## Troubleshooting API Registration

### Issue: Backend endpoint unreachable

**Error**: 
```
Failed to invoke API endpoint. Backend service is unreachable.
```

**Solution**:
- Verify backend container is running: `docker ps | grep cms-backend`
- Check backend service health: `curl http://localhost:8000/health`
- Ensure Docker network connectivity: `docker network inspect cms-platform-net`

### Issue: CORS errors from frontend

**Error**: 
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution**:
1. In APIM Publisher, add CORS policy:
   ```
   Access-Control-Allow-Origin: *
   Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
   Access-Control-Allow-Headers: Authorization, Content-Type
   ```
2. Update frontend CORS configuration if using direct backend calls

### Issue: Certificate validation errors

**Error**: 
```
SSL certificate problem: self signed certificate
```

**Solution** (for development only):
- Use `curl -k` flag to skip certificate validation
- In frontend, set `rejectUnauthorized: false` for dev environments
- In production, use proper SSL certificates

### Issue: OAuth2 token expired

**Error**: 
```
401 Unauthorized: Access token expired
```

**Solution**:
- Implement token refresh logic in frontend
- Request new token before expiration
- Store token expiration time and refresh automatically

## API Versioning Strategy

Maintain multiple API versions for backward compatibility:

```
Version 1.0: /cms/v1/test       (initial release)
Version 1.1: /cms/v1.1/test     (with new fields)
Version 2.0: /cms/v2/test       (breaking changes)
```

## Production Deployment Checklist

- [ ] Replace self-signed SSL certificates
- [ ] Change admin password from default
- [ ] Enable database backups
- [ ] Configure rate limiting/throttling tiers
- [ ] Set up monitoring and alerting
- [ ] Configure log rotation
- [ ] Implement API analytics collection
- [ ] Set up API versioning strategy
- [ ] Document API changes
- [ ] Train development team

## Additional Resources

- [WSO2 APIM Publisher Guide](https://apim.docs.wso2.com/en/4.1.0/design/create-api/create-rest-api/create-a-rest-api/)
- [OAuth2 Implementation](https://apim.docs.wso2.com/en/4.1.0/design/api-security/oauth2/)
- [Rate Limiting](https://apim.docs.wso2.com/en/4.1.0/design/rate-limiting/introduction-to-throttling/)
- [API Analytics](https://apim.docs.wso2.com/en/4.1.0/observe/api-analytics/overview-api-analytics/)

## Support & Documentation

For more information:
- WSO2 APIM Documentation: https://apim.docs.wso2.com/
- Community Forum: https://stackoverflow.com/questions/tagged/wso2-apim
- Issue Tracker: https://github.com/GitsCodelab/CMS-Platform/issues
