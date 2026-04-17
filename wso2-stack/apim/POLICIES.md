# WSO2 API Manager - Default Policies for CMS Platform

This file documents the recommended policies to apply to CMS Platform APIs in WSO2 APIM.

## Policies Configuration

### 1. Authentication Policy

**Type**: OAuth2 / API Key

Apply to all APIs to ensure only authorized clients can access endpoints.

**Configuration**:
```
Authentication Type: OAuth2
OAuth2 Scopes:
  - cms:read (for GET operations)
  - cms:write (for POST, PUT operations)
  - cms:delete (for DELETE operations)
```

### 2. Throttling Policy

**Type**: Rate Limiting / Throttle

Prevent API abuse by limiting requests per client.

**Configuration**:
```
Tier: Gold (default)
  - Requests per minute: 1000
  - Requests per day: 100,000

Tier: Silver (for non-critical users)
  - Requests per minute: 100
  - Requests per day: 10,000

Tier: Bronze (for public endpoints)
  - Requests per minute: 10
  - Requests per day: 1,000
```

### 3. CORS Policy

**Type**: CORS

Allow cross-origin requests from the frontend.

**Configuration**:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type, X-API-Key
Access-Control-Max-Age: 3600
Access-Control-Allow-Credentials: true
```

### 4. Request/Response Transformation

**Type**: Mediation Policy

Transform request/response format.

**Use Cases**:
- Add request tracking ID
- Transform response format
- Remove sensitive headers
- Log API access

### 5. Security Policy

**Type**: API Security

**Configuration**:
```
Transport Security: HTTPS Only
Certificate Validation: Required
Request Validation: Enabled
Response Validation: Enabled
```

### 6. Logging & Analytics

**Type**: Analytics

Enable detailed logging for audit trail.

**Configuration**:
```
Log Request Payload: Enabled
Log Response Payload: Enabled (exclude sensitive data)
Log Headers: Enabled
Log Authentication Info: Enabled
Analytics Event Publishing: Enabled
```

## Per-API Policy Recommendations

### Oracle Test API (`/cms/oracle/test`)

```yaml
Throttle Tier: Gold
Authentication: OAuth2 (cms:read, cms:write, cms:delete)
CORS: Enabled
Request Transform: 
  - Add X-Request-ID header
Response Transform:
  - Normalize Oracle timestamps
Logging: Full request/response logging
```

### PostgreSQL Test API (`/cms/postgres/test`)

```yaml
Throttle Tier: Gold
Authentication: OAuth2 (cms:read, cms:write, cms:delete)
CORS: Enabled
Request Transform: 
  - Add X-Request-ID header
Response Transform:
  - Ensure consistent JSON format
Logging: Full request/response logging
```

## Scopes Definition

Define custom scopes for fine-grained access control:

| Scope | Description | Operations |
|-------|-------------|-----------|
| `cms:read` | Read-only access | GET all, GET by ID |
| `cms:write` | Create/update records | POST, PUT |
| `cms:delete` | Delete records | DELETE |
| `cms:admin` | Full administrative access | All operations |

## Rate Limiting Strategy

### By User Tier

- **Premium**: 1000 req/min (100K per day)
- **Standard**: 100 req/min (10K per day)
- **Free**: 10 req/min (1K per day)

### By Endpoint

- **GET /test**: 5000 req/min (read-heavy)
- **POST /test**: 500 req/min (write-protected)
- **DELETE /test**: 50 req/min (dangerous operation)

## Backend Service URL Configuration

For both production and sandbox environments:

```
Backend URL: http://cms-backend:8000

Endpoints:
  - Oracle: http://cms-backend:8000/oracle
  - PostgreSQL: http://cms-backend:8000/postgres
```

## Frontend Integration

Update frontend API client to route through WSO2 APIM:

```javascript
// Before: Direct backend call
const api = axios.create({
  baseURL: 'http://localhost:8000'
});

// After: Through APIM gateway
const api = axios.create({
  baseURL: 'https://localhost:8243/cms/v1'
});

// Add token injection
api.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

## Health Check & Monitoring

Configure health check endpoint:

```
Path: /health
Method: GET
Expected Response: 
{
  "status": "healthy",
  "api": "CMS Platform API",
  "version": "1.0.0"
}
```

## Troubleshooting Policy Issues

### 401 Unauthorized
- Verify OAuth2 token is valid
- Check token scope covers required operations
- Ensure token is not expired

### 429 Too Many Requests
- Check current throttle tier
- Request higher tier if needed
- Implement exponential backoff in client

### 403 Forbidden
- Verify user has required OAuth2 scope
- Check API subscription status
- Ensure user is in correct user group

### 500 Backend Error
- Check backend service health
- Verify PostgreSQL/Oracle connectivity
- Review backend logs
- Check network routing in Docker

## Policy Management Commands

**Export API policies:**
```bash
curl -X GET "https://localhost:9443/api/am/publisher/v1/apis/{api-id}/policies" \
  -H "Authorization: Bearer {access-token}"
```

**Update API policies:**
```bash
curl -X PUT "https://localhost:9443/api/am/publisher/v1/apis/{api-id}" \
  -H "Content-Type: application/json" \
  --data @cms-api-definition.json
```

## Security Best Practices

1. **Always use HTTPS**: Enable SSL/TLS for all API communication
2. **Rotate Keys**: Change default APIM credentials immediately
3. **Audit Logs**: Monitor API access logs for suspicious activity
4. **Token Expiration**: Set reasonable token expiration times (15-60 min)
5. **Rate Limiting**: Prevent brute force and DoS attacks
6. **Input Validation**: APIM validates against schema before routing
7. **Sensitive Data**: Mask PII in logs and monitoring
8. **API Versioning**: Use versioning for backward compatibility

## References

- [WSO2 APIM Policy Management](https://apim.docs.wso2.com/en/4.1.0/design/policies/overview/)
- [OAuth2 Scopes](https://apim.docs.wso2.com/en/4.1.0/design/api-security/oauth2-scopes/)
- [Throttling Policies](https://apim.docs.wso2.com/en/4.1.0/design/rate-limiting/)
