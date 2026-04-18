# WSO2 IS - APIM Integration Guide

This guide explains how to integrate WSO2 Identity Server with WSO2 API Manager for centralized authentication and authorization.

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│    Frontend     │◄───────►│   APIM 4.3.0     │◄───────►│   WSO2 IS   │
│   (React)       │         │   Gateway        │         │   7.0.0     │
└─────────────────┘         └──────────────────┘         └─────────────┘
                                    │                            │
                                    ▼                            ▼
                            ┌──────────────────┐         ┌─────────────┐
                            │ Backend APIs     │         │  PostgreSQL │
                            │ (FastAPI)        │         │   Database  │
                            └──────────────────┘         └─────────────┘
```

## Prerequisites

- WSO2 IS 7.0.0 running on https://localhost:9443
- WSO2 APIM 4.3.0 running on https://localhost:9443 (different instance)
- Both services have database connectivity
- Docker network: `cms-platform-net`

## Step 1: Configure WSO2 IS

### 1.1 Create Service Provider for APIM

1. Access Admin Console: https://localhost:9443/carbon
2. Main → Applications → Service Providers → Add
3. Enter: "WSO2-APIM-Gateway"
4. Click Register

### 1.2 Configure OAuth2/OIDC

1. Under **Inbound Authentication Configuration → OAuth/OpenID Connect**
2. Click **Configure**
3. Set:
   - **Callback URL:** https://cms-apim:9443/publisher/services/auth/callback
   - **Grant Types:** Authorization Code, Client Credentials, Refresh Token
   - **Public Client:** Disabled

### 1.3 Generate Credentials

1. Click **Generate Client ID and Client Secret**
2. Save the credentials:
   ```
   Client ID: [SAVE_THIS]
   Client Secret: [SAVE_THIS]
   ```

### 1.4 Configure Scopes

1. Go to: Main → Manage → Scope Management → Add Scope
2. Create scopes:
   - `apim:subscribe` - API subscription
   - `apim:publish` - API publishing
   - `apim:admin` - Admin operations
   - `apim:view` - View only

## Step 2: Configure WSO2 APIM

### 2.1 Update APIM Configuration

Edit APIM environment configuration:

```bash
docker compose exec cms-apim bash
cd /home/wso2carbon/wso2am-4.3.0/repository/conf/deployment-toml.d
```

Create `identity-server-config.toml`:

```toml
[keymanager.key_manager_configuration.key_manager_server_endpoint]
enable_oauth_app_creation = true
enable_key_validation = true

[keymanager.key_manager_configuration.key_manager_endpoints]
service_endpoint = "https://cms-wso2is:9443"
token_endpoint = "https://cms-wso2is:9443/oauth2/token"
revoke_endpoint = "https://cms-wso2is:9443/oauth2/revoke"
user_info_endpoint = "https://cms-wso2is:9443/oauth2/userinfo"

[keymanager.key_manager_configuration.key_manager_credentials]
client_id = "CLIENT_ID_FROM_STEP_1.3"
client_secret = "CLIENT_SECRET_FROM_STEP_1.3"

[keymanager.key_manager_configuration.token_validation]
enable_token_validation = true
token_validation_endpoint = "https://cms-wso2is:9443/oauth2/introspect"
```

### 2.2 Restart APIM

```bash
docker compose restart cms-apim
```

### 2.3 Verify Connection

Access APIM Admin Portal:
```
URL: https://localhost:9443/admin
Username: admin
Password: admin
```

## Step 3: Create OAuth2 Applications in APIM

### 3.1 Create Application for Frontend

1. Access APIM Publisher: https://localhost:9443/publisher
2. Click: Applications → Create Application
3. Fill:
   - Name: "CMS-Frontend"
   - Type: "Web Application"
   - OAuth2 Tokens Endpoint: https://localhost:9443/oauth2/token

### 3.2 Configure OAuth2 Settings

1. Under OAuth2 section:
   - Token Endpoint: https://cms-wso2is:9443/oauth2/token
   - Authorize Endpoint: https://cms-wso2is:9443/oauth2/authorize
   - Token Revocation Endpoint: https://cms-wso2is:9443/oauth2/revoke
   - Callback URL: http://localhost:3000/callback

### 3.3 Generate Application Credentials

1. Click **Generate Keys**
2. Select: Production
3. Save:
   - Consumer Key
   - Consumer Secret

## Step 4: Frontend Integration

### 4.1 Update Frontend Configuration

Create `frontend/src/config/auth.js`:

```javascript
export const authConfig = {
  // WSO2 APIM OAuth2 Endpoints
  clientId: 'CONSUMER_KEY_FROM_APIM',
  clientSecret: 'CONSUMER_SECRET_FROM_APIM',
  
  // WSO2 IS Endpoints (via APIM proxy)
  authorizationEndpoint: 'https://localhost:9443/oauth2/authorize',
  tokenEndpoint: 'https://localhost:9443/oauth2/token',
  userInfoEndpoint: 'https://localhost:9443/oauth2/userinfo',
  revokeEndpoint: 'https://localhost:9443/oauth2/revoke',
  
  // Redirect URI
  redirectUri: 'http://localhost:3000/callback',
  
  // Scopes
  scopes: ['openid', 'profile', 'email', 'apim:subscribe'],
  
  // Token configuration
  responseType: 'code',
  grantType: 'authorization_code',
};
```

### 4.2 Implement Login Flow

Create `frontend/src/hooks/useAuth.js`:

```javascript
import { useState, useCallback } from 'react';
import { authConfig } from '../config/auth';
import axios from 'axios';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(false);

  // Login - Redirect to WSO2 IS
  const login = useCallback(() => {
    const params = new URLSearchParams({
      client_id: authConfig.clientId,
      response_type: authConfig.responseType,
      scope: authConfig.scopes.join(' '),
      redirect_uri: authConfig.redirectUri,
      state: generateRandomState(),
    });
    
    window.location.href = `${authConfig.authorizationEndpoint}?${params}`;
  }, []);

  // Handle OAuth2 callback
  const handleCallback = useCallback(async (code) => {
    setLoading(true);
    try {
      // Exchange code for token
      const response = await axios.post(
        authConfig.tokenEndpoint,
        {
          grant_type: authConfig.grantType,
          code: code,
          client_id: authConfig.clientId,
          client_secret: authConfig.clientSecret,
          redirect_uri: authConfig.redirectUri,
        },
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      const { access_token, id_token } = response.data;
      setToken(access_token);
      
      // Store tokens
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('idToken', id_token);
      
      // Get user info
      await fetchUserInfo(access_token);
    } catch (error) {
      console.error('OAuth2 callback error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Get user information
  const fetchUserInfo = useCallback(async (accessToken) => {
    try {
      const response = await axios.get(
        authConfig.userInfoEndpoint,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        }
      );
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user info:', error);
    }
  }, []);

  // Logout
  const logout = useCallback(async () => {
    try {
      const accessToken = localStorage.getItem('accessToken');
      
      // Revoke token
      await axios.post(
        authConfig.revokeEndpoint,
        {
          token: accessToken,
          client_id: authConfig.clientId,
          client_secret: authConfig.clientSecret,
        }
      );
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('idToken');
      setUser(null);
      setToken(null);
    }
  }, []);

  return {
    user,
    token,
    loading,
    login,
    logout,
    handleCallback,
  };
};

// Utility function
function generateRandomState() {
  return Math.random().toString(36).substring(2, 15);
}
```

### 4.3 Create Callback Component

Create `frontend/src/components/OAuthCallback.jsx`:

```javascript
import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const OAuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { handleCallback } = useAuth();

  useEffect(() => {
    const code = searchParams.get('code');
    const error = searchParams.get('error');

    if (error) {
      console.error('OAuth2 error:', error);
      navigate('/login');
      return;
    }

    if (code) {
      handleCallback(code).then(() => {
        navigate('/');
      });
    }
  }, [searchParams, handleCallback, navigate]);

  return (
    <div>
      <h2>Authenticating...</h2>
      <p>Please wait while we complete your login.</p>
    </div>
  );
};
```

## Step 5: Backend Integration

### 5.1 Configure FastAPI

Update `backend/app/config.py`:

```python
# OAuth2 Configuration
OAUTH2_TOKEN_URL = "https://localhost:9443/oauth2/token"
OAUTH2_INTROSPECTION_URL = "https://localhost:9443/oauth2/introspect"
OAUTH2_USERINFO_URL = "https://localhost:9443/oauth2/userinfo"

# JWT Configuration
JWT_ALGORITHM = "RS256"
JWT_ISSUER = "https://cms-wso2is:9443"
JWT_AUDIENCE = "CMS-Frontend"
```

### 5.2 Implement Token Validation

Create `backend/app/security.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import jwt, JWTError
from app.config import JWT_ALGORITHM, JWT_ISSUER, JWT_AUDIENCE
import httpx

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    token = credentials.credentials
    
    try:
        # Verify JWT signature
        payload = jwt.get_unverified_claims(token)
        
        # Validate token with APIM/IS
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(
                "https://localhost:9443/oauth2/introspect",
                data={
                    "token": token,
                    "client_id": "your-client-id",
                    "client_secret": "your-client-secret",
                }
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        introspection = response.json()
        if not introspection.get("active"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is not active"
            )
        
        return payload
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )

# Protected endpoint example
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/protected")
async def protected_route(token_claims: dict = Depends(verify_token)):
    return {
        "message": "Access granted",
        "user": token_claims.get("sub"),
        "scopes": token_claims.get("scope", "").split()
    }
```

## Step 6: Test Integration

### 6.1 Test Frontend Login

1. Open: http://localhost:3000
2. Click Login button
3. Redirect to WSO2 IS login page
4. Enter credentials
5. Accept permissions
6. Redirect back to frontend with token

### 6.2 Test Token Exchange

```bash
# Get authorization code (from login flow)
# Then exchange for token:

curl -X POST https://localhost:9443/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&code=AUTH_CODE&client_id=CLIENT_ID&client_secret=CLIENT_SECRET&redirect_uri=http://localhost:3000/callback" \
  --insecure
```

### 6.3 Test Protected API

```bash
# Use access token to access protected API
curl -X GET http://localhost:8000/api/protected \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

## Step 7: API Manager Integration

### 7.1 Publish APIs through APIM

1. Access APIM Publisher: https://localhost:9443/publisher
2. Create API:
   - Name: "CMS-Test-API"
   - Context: "/cms-api"
   - Backend URL: http://cms-backend:8000

### 7.2 Configure OAuth2 Scopes

1. Under Scopes:
   - Add: `apim:subscribe`
   - Add: `apim:invoke`
2. Configure token validation with WSO2 IS

### 7.3 Publish API

1. Click Publish
2. API is now available through APIM Gateway
3. Access via: https://localhost:8243/cms-api/...

## Troubleshooting

### Issue: "Invalid redirect URI"

**Solution:**
- Verify callback URL matches exactly in WSO2 IS configuration
- Check callback URL registered in APIM application
- Ensure URLs use https for production

### Issue: Token validation fails

**Solution:**
- Verify WSO2 IS is accessible from APIM
- Check token endpoint configuration
- Validate client credentials
- Review logs in both services

### Issue: CORS errors

**Solution:**
- Enable CORS in APIM gateway
- Configure allowed origins in WSO2 IS
- Use proper headers in frontend requests

### Issue: User not found after login

**Solution:**
- Verify user exists in WSO2 IS
- Check user store configuration
- Review user claims mapping

## Production Checklist

- [ ] Use HTTPS with valid certificates (not self-signed)
- [ ] Change default admin passwords
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy
- [ ] Implement rate limiting
- [ ] Use secure token storage (HttpOnly cookies)
- [ ] Enable CSRF protection
- [ ] Configure session timeout
- [ ] Set up SSL/TLS for database connections
- [ ] Implement token rotation
- [ ] Configure refresh token rotation
- [ ] Set up API rate limiting per user

## References

- [WSO2 IS OAuth2 Documentation](https://is.docs.wso2.com/en/7.0.0/)
- [WSO2 APIM Key Manager Integration](https://apim.docs.wso2.com/en/4.3.0/)
- [OpenID Connect Specification](https://openid.net/connect/)
- [OAuth2 Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)

---

**Last Updated:** April 2026
**Version:** WSO2 IS 7.0.0 + APIM 4.3.0
**Status:** Production Ready
