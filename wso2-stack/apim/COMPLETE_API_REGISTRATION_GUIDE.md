# WSO2 APIM - Complete API Registration Guide for CMS Backend

This guide provides step-by-step instructions to register the CMS Platform backend APIs in WSO2 API Manager.

## API Overview

**Backend URLs:**
- **Base URL:** `http://cms-backend:8000` (inside Docker network)
- **Local URL:** `http://localhost:8000` (from host machine)

**Available Endpoints:**
- `/oracle/test` - Oracle database CRUD operations
- `/postgres/test` - PostgreSQL database CRUD operations
- `/health` - Health check endpoint

---

## Part 1: Create the CMS Test API

### Step 1: Access Publisher Portal

1. Open browser and navigate to: **https://localhost:9443/publisher**
2. You may see a security warning (self-signed certificate):
   - Click **Advanced** 
   - Click **Proceed to localhost (unsafe)**
3. Login with credentials:
   - **Username:** `admin`
   - **Password:** `admin`

### Step 2: Create New API

1. Click the **Create** button (top-left)
2. Select **Design a new REST API**
3. Fill in the Basic Information form:

```
API Name:        CMS Test API
Context:         /cms
API Version:     1.0.0
Endpoint Type:   HTTP (Default)
Backend Endpoint: http://cms-backend:8000
```

4. Click **Create & Publish**

**Visual walkthrough:**
```
Publisher Portal
├── Click [Create] button
├── Select "Design a new REST API"
├── Fill Form:
│   ├── API Name: CMS Test API
│   ├── Context: /cms
│   ├── API Version: 1.0.0
│   └── Backend Endpoint: http://cms-backend:8000
└── Click [Create & Publish]
```

### Step 3: Define API Resources

Once the API is created, you'll see the API editor. Now add resources:

**Resource 1: Oracle Test Data**

1. Click **Resources** tab
2. Click **+ Add Resource**
3. Configure:
   - **URL Pattern:** `/oracle/test`
   - **Methods:** GET, POST, PUT, DELETE

4. Click **Add Resource**

**Resource 2: PostgreSQL Test Data**

1. Click **+ Add Resource** again
2. Configure:
   - **URL Pattern:** `/postgres/test`
   - **Methods:** GET, POST, PUT, DELETE

3. Click **Add Resource**

**Resource 3: Health Check (Optional)**

1. Click **+ Add Resource** 
2. Configure:
   - **URL Pattern:** `/health`
   - **Methods:** GET

3. Click **Add Resource**

---

## Part 2: Configure API Endpoints

### Step 1: Set Production & Sandbox Endpoints

1. In the API editor, click **Endpoints** tab
2. Ensure the following are set:

```
Production Endpoint:  http://cms-backend:8000
Sandbox Endpoint:     http://cms-backend:8000
```

3. Click **Save**

### Step 2: Test Backend Connectivity

1. Click **Test Console** (or **Try-it-out**)
2. Expand `GET /health`
3. Click **Try It Out**
4. Expected response:
```json
{
  "status": "healthy",
  "api": "CMS Platform API",
  "version": "1.0.0"
}
```

If you see the health check response, your backend connection is working correctly!

---

## Part 3: Apply Security Policies

### Step 1: Configure Authentication

1. In the API editor, click **Policies** or **Security** tab
2. Under **API Security**, enable:
   - ✓ **API Key Authentication** (for simple testing)
   - ✓ **OAuth2 Authentication** (for production)

### Step 2: Configure Throttling

1. Click **Throttling** section
2. Select **Gold Tier**:
   - **Requests per Minute:** 1000
   - **Requests per Day:** 100,000
3. Click **Save**

### Step 3: Enable CORS (Cross-Origin)

1. Scroll to **CORS** policy
2. Enable CORS with:
   - **Access-Control-Allow-Origin:** `*`
   - **Access-Control-Allow-Methods:** GET, POST, PUT, DELETE, OPTIONS
   - **Access-Control-Allow-Headers:** Authorization, Content-Type, X-API-Key

3. Click **Save**

---

## Part 4: Publish the API

### Step 1: Publish to Gateway

1. In the API editor, click the **Publish** button (top-right)
2. Confirm publication
3. You should see: **"API published successfully"**

### Step 2: Verify Publication

1. Navigate to **https://localhost:9443/publisher**
2. Find **CMS Test API** in the API list
3. Status should show: **Published**

---

## Part 5: Access via Developer Portal

### Step 1: Subscribe to the API

1. Navigate to **https://localhost:9443/devportal**
2. Login with credentials (admin/admin) or create new account
3. Find **CMS Test API 1.0.0** in the catalog
4. Click the API card
5. Click **Subscribe** button
6. Select or create an application:
   - **Application Name:** CMS Frontend App
   - Click **Subscribe**

### Step 2: Get API Key & Access Token

1. Click **My Subscriptions**
2. Find **CMS Test API** subscription
3. Click the subscription
4. Click **Production Keys** tab
5. You'll see:
   - **Consumer Key** (Client ID)
   - **Consumer Secret** (Client Secret)
   - **Generate Access Token** button

6. Click **Generate Access Token**
7. Copy the generated **Access Token**

---

## Part 6: Test the API

### Option A: Using cURL

**Test with Direct API Key:**

```bash
# Get API Key
API_KEY="your-api-key-here"

# Test GET (Oracle database)
curl -X GET "https://localhost:8243/cms/1.0.0/oracle/test" \
  -H "X-API-Key: $API_KEY" \
  -k

# Test GET (PostgreSQL database)
curl -X GET "https://localhost:8243/cms/1.0.0/postgres/test" \
  -H "X-API-Key: $API_KEY" \
  -k
```

**Test with OAuth2 Token:**

```bash
# Generate OAuth2 Token
TOKEN=$(curl -X POST "https://localhost:9443/oauth2/token" \
  -H "Authorization: Basic YWRtaW46YWRtaW4=" \
  -d "grant_type=client_credentials" \
  -k -s | jq -r '.access_token')

# Test with Bearer token
curl -X GET "https://localhost:8243/cms/1.0.0/oracle/test" \
  -H "Authorization: Bearer $TOKEN" \
  -k
```

**Create a new record:**

```bash
curl -X POST "https://localhost:8243/cms/1.0.0/oracle/test" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "name": "Test Record",
    "description": "Created via APIM",
    "status": "active"
  }' \
  -k
```

### Option B: Using Postman

**Import CMS API to Postman:**

1. In WSO2 Publisher, go to API details
2. Click **Download** → **Swagger/OpenAPI**
3. In Postman:
   - Click **Import**
   - Paste the Swagger/OpenAPI definition
   - Postman auto-creates collection

**Configure Authentication:**

1. Go to **Collection Settings**
2. Click **Authorization** tab
3. Select **API Key** or **Bearer Token**
4. Add the key/token you generated

**Test Requests:**

```
GET https://localhost:8243/cms/1.0.0/oracle/test
Headers: X-API-Key: [your-key]

POST https://localhost:8243/cms/1.0.0/oracle/test
Headers: 
  - X-API-Key: [your-key]
  - Content-Type: application/json
Body:
{
  "id": 1,
  "name": "Test",
  "description": "Test description",
  "status": "active"
}
```

### Option C: Using APIM Try-It-Out

1. In Publisher, go to **API Details**
2. Click **Try-it-out** tab
3. Select operation (e.g., `GET /oracle/test`)
4. Click **Try it**
5. View response

---

## Part 7: API Gateway Endpoints

Once published, your API is accessible via the gateway:

```
HTTP:  http://localhost:8280/cms/1.0.0
HTTPS: https://localhost:8243/cms/1.0.0
```

**Available Operations:**

```
GET    /cms/1.0.0/oracle/test           - Get all Oracle records
GET    /cms/1.0.0/oracle/test/{id}      - Get specific Oracle record
POST   /cms/1.0.0/oracle/test           - Create new Oracle record
PUT    /cms/1.0.0/oracle/test/{id}      - Update Oracle record
DELETE /cms/1.0.0/oracle/test/{id}      - Delete Oracle record

GET    /cms/1.0.0/postgres/test         - Get all PostgreSQL records
GET    /cms/1.0.0/postgres/test/{id}    - Get specific PostgreSQL record
POST   /cms/1.0.0/postgres/test         - Create new PostgreSQL record
PUT    /cms/1.0.0/postgres/test/{id}    - Update PostgreSQL record
DELETE /cms/1.0.0/postgres/test/{id}    - Delete PostgreSQL record

GET    /cms/1.0.0/health                - Health check
```

---

## Part 8: Update Frontend to Use APIM Gateway

### Update Frontend API Client

**File:** `frontend/src/api/client.js`

```javascript
import axios from 'axios';

// Create API client with APIM gateway
const apiClient = axios.create({
  baseURL: 'https://localhost:8243/cms/1.0.0',
  timeout: 5000,
  httpsAgent: {
    rejectUnauthorized: false  // For development only!
  }
});

// Add API Key injection
apiClient.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('apiKey');
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey;
  }
  
  // Or use OAuth2 Bearer token
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  
  return config;
});

// Handle 401 Unauthorized
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token/Key expired - redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Export separate endpoints
export const oracleAPI = {
  getAll: () => apiClient.get('/oracle/test'),
  getById: (id) => apiClient.get(`/oracle/test/${id}`),
  create: (data) => apiClient.post('/oracle/test', data),
  update: (id, data) => apiClient.put(`/oracle/test/${id}`, data),
  delete: (id) => apiClient.delete(`/oracle/test/${id}`)
};

export const postgresAPI = {
  getAll: () => apiClient.get('/postgres/test'),
  getById: (id) => apiClient.get(`/postgres/test/${id}`),
  create: (data) => apiClient.post('/postgres/test', data),
  update: (id, data) => apiClient.put(`/postgres/test/${id}`, data),
  delete: (id) => apiClient.delete(`/postgres/test/${id}`)
};

export default apiClient;
```

### Update Frontend Hooks

**File:** `frontend/src/hooks/useOracle.js`

```javascript
import { useState, useEffect } from 'react';
import { oracleAPI } from '../api/client';

export const useOracle = () => {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecords = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await oracleAPI.getAll();
      const data = Array.isArray(response.data) 
        ? response.data 
        : response.data.data || [];
      setRecords(normalizeRecords(data));
    } catch (err) {
      setError(err.message || 'Failed to fetch records');
    } finally {
      setLoading(false);
    }
  };

  const createRecord = async (data) => {
    try {
      await oracleAPI.create(data);
      await fetchRecords(); // Refresh list
    } catch (err) {
      setError(err.message || 'Failed to create record');
      throw err;
    }
  };

  const updateRecord = async (id, data) => {
    try {
      await oracleAPI.update(id, data);
      await fetchRecords(); // Refresh list
    } catch (err) {
      setError(err.message || 'Failed to update record');
      throw err;
    }
  };

  const deleteRecord = async (id) => {
    try {
      await oracleAPI.delete(id);
      await fetchRecords(); // Refresh list
    } catch (err) {
      setError(err.message || 'Failed to delete record');
      throw err;
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  return { records, loading, error, fetchRecords, createRecord, updateRecord, deleteRecord };
};

// Normalize record fields (Oracle returns uppercase)
const normalizeRecords = (records) => {
  return records.map(record => ({
    id: record.id || record.ID,
    name: record.name || record.NAME,
    description: record.description || record.DESCRIPTION,
    status: record.status || record.STATUS
  }));
};
```

---

## Troubleshooting

### Issue: Backend endpoint unreachable

**Error message:**
```
Failed to invoke endpoint. Backend service is unreachable.
```

**Solutions:**
1. Verify backend is running: `docker ps | grep cms-backend`
2. Test backend health: `curl http://localhost:8000/health`
3. Check Docker network: `docker network inspect cms-platform-net`
4. Verify endpoint URL in APIM is: `http://cms-backend:8000`

### Issue: API Key not working

**Error message:**
```
401 Unauthorized
```

**Solutions:**
1. Verify API Key is enabled in Publisher → Security
2. Generate new key in DevPortal → My Subscriptions
3. Ensure key is passed in header: `X-API-Key: [key-value]`
4. Check key hasn't expired

### Issue: CORS errors from frontend

**Error message:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solutions:**
1. Enable CORS policy in Publisher → Policies
2. Set `Access-Control-Allow-Origin: *`
3. Allow required headers: Authorization, Content-Type, X-API-Key
4. Verify frontend is calling through APIM gateway (not direct backend)

### Issue: SSL certificate errors

**Error message:**
```
SSL certificate problem: self signed certificate
```

**Solutions:**
1. In development: Use `https -k` flag with curl
2. In Postman: Disable SSL verification (Settings → SSL verification)
3. In frontend: Set `rejectUnauthorized: false` in httpsAgent
4. In production: Install CA-signed certificate

### Issue: API returns 404

**Error message:**
```
404 Not Found
```

**Solutions:**
1. Verify resource path is correct: `/oracle/test` not `/oracletest`
2. Check HTTP method (GET, POST, PUT, DELETE)
3. Verify API is published (not just saved)
4. Test direct backend endpoint: `curl http://localhost:8000/oracle/test`

---

## API Testing Examples

### Complete Test Workflow

```bash
#!/bin/bash

# 1. Generate OAuth2 Token
echo "Generating OAuth2 token..."
TOKEN=$(curl -s -X POST "https://localhost:9443/oauth2/token" \
  -H "Authorization: Basic YWRtaW46YWRtaW4=" \
  -d "grant_type=client_credentials" \
  -k | jq -r '.access_token')

echo "Token: $TOKEN"
echo ""

# 2. Test Health Check
echo "Testing health check..."
curl -X GET "https://localhost:8243/cms/1.0.0/health" \
  -H "Authorization: Bearer $TOKEN" \
  -k -s | jq '.'
echo ""

# 3. Get all Oracle records
echo "Fetching Oracle records..."
curl -X GET "https://localhost:8243/cms/1.0.0/oracle/test" \
  -H "Authorization: Bearer $TOKEN" \
  -k -s | jq '.'
echo ""

# 4. Create new record
echo "Creating new Oracle record..."
curl -X POST "https://localhost:8243/cms/1.0.0/oracle/test" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "name": "APIM Test Record",
    "description": "Created through APIM gateway",
    "status": "active"
  }' \
  -k -s | jq '.'
echo ""

# 5. Get PostgreSQL records
echo "Fetching PostgreSQL records..."
curl -X GET "https://localhost:8243/cms/1.0.0/postgres/test" \
  -H "Authorization: Bearer $TOKEN" \
  -k -s | jq '.'
```

---

## Next Steps

1. ✅ Register the API in WSO2 APIM (follow steps above)
2. ✅ Test API through APIM gateway (using cURL or Postman)
3. ✅ Update frontend to use APIM gateway endpoints
4. ✅ Generate and store API keys/tokens in frontend
5. ✅ Deploy to production with real SSL certificates
6. ✅ Monitor API usage through APIM Analytics
7. ✅ Configure rate limiting and policies as needed

---

## Additional Resources

- [WSO2 APIM Documentation](https://apim.docs.wso2.com/)
- [REST API Development Guide](https://apim.docs.wso2.com/en/4.0.0/design/create-api/create-rest-api/)
- [API Security & Policies](https://apim.docs.wso2.com/en/4.0.0/design/policies/overview/)
- [OAuth2 Implementation](https://apim.docs.wso2.com/en/4.0.0/design/api-security/oauth2/)
- [API Analytics](https://apim.docs.wso2.com/en/4.0.0/observe/api-analytics/)
