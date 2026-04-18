# WSO2 Identity Server (IS) Setup Guide

WSO2 Identity Server is an enterprise-grade identity management and access control platform. It provides centralized user authentication, authorization, single sign-on (SSO), and OAuth2/OpenID Connect identity federation.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- PostgreSQL running (cms-postgresql)
- Linux/WSL2 environment

### Startup

```bash
# Make the startup script executable
chmod +x start.sh

# Start WSO2 IS
./start.sh

# Or manually start with docker compose
docker compose up -d cms-wso2is
```

### Access Points

| Portal | URL | Purpose |
|--------|-----|---------|
| Admin Console | https://localhost:9443/carbon | Manage users, roles, applications |
| Account Portal | https://localhost:9443/accountportal | User self-service portal |
| API Docs | https://localhost:9443/api-docs | REST API documentation |
| Playground | https://localhost:9443/playground | OAuth2/OIDC playground |

**Default Credentials:**
- Username: `admin`
- Password: `admin`

> **Important:** Change default credentials in production!

## 📋 Key Features

✅ **User Management**
- Create, update, delete user accounts
- Role-based access control (RBAC)
- User profile management
- Multi-tenant support

✅ **Authentication**
- Local authentication
- LDAP/Active Directory integration
- Multi-factor authentication (MFA)
- Passwordless authentication

✅ **Authorization**
- OAuth2.0 authorization
- OpenID Connect (OIDC)
- SAML2.0 SSO
- Attribute-based access control (ABAC)

✅ **API Security**
- API scopes and permissions
- Application-to-user scopes
- Audience restrictions
- Token revocation

✅ **Developer Portal**
- Application registration
- Key generation and management
- API subscriptions
- Usage analytics

## 🔧 Configuration

### Database

WSO2 IS uses PostgreSQL for storing:
- User accounts and credentials
- Application metadata
- OAuth2 tokens and scopes
- API configurations
- Audit logs

**Database Details:**
```
Host: cms-postgresql
Port: 5432
Database: wso2is
User: postgres
Password: postgres
```

### Environment Variables

Edit `.env` file to customize:

```env
# Database
DB_HOSTNAME=cms-postgresql
DB_NAME=wso2is

# Admin Credentials (CHANGE IN PRODUCTION)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin

# Server Hostname
HOSTNAME=cms-wso2is
PORT=9443

# Optional: LDAP
LDAP_ENABLED=false
LDAP_URL=ldap://ldap-server:389

# Optional: Email (for password recovery)
SMTP_ENABLED=false
SMTP_HOST=smtp.example.com
```

## 🔐 OAuth2 & OpenID Connect Setup

### Creating an Application

1. **Access Admin Console**
   - Navigate to https://localhost:9443/carbon
   - Login with admin credentials

2. **Create Service Provider**
   - Go to: Main → Applications → Add
   - Enter application name (e.g., "CMS-Platform")
   - Configure OAuth2/OIDC settings

3. **Configure OAuth2 Scopes**
   ```
   Scopes:
   - openid (identity)
   - profile (user profile)
   - email (email address)
   - api (API access)
   ```

4. **Generate Credentials**
   - Generate Client ID & Client Secret
   - Save for application configuration

### Token Generation Flow

```bash
# Get access token
curl -X POST https://localhost:9443/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&scope=api"

# Response
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### User Authentication Flow

```bash
# Authorization endpoint
https://localhost:9443/oauth2/authorize?
  client_id=YOUR_CLIENT_ID&
  response_type=code&
  scope=openid%20profile%20email&
  redirect_uri=http://localhost:3000/callback

# Token endpoint (after receiving authorization code)
curl -X POST https://localhost:9443/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&code=AUTH_CODE&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&redirect_uri=http://localhost:3000/callback"
```

## 👥 User Management

### Create User via API

```bash
curl -X POST https://localhost:9443/api/users \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "userName": "john.doe",
    "password": "SecurePass123!",
    "emails": ["john@example.com"],
    "givenName": "John",
    "familyName": "Doe",
    "active": true
  }'
```

### Assign Role to User

```bash
curl -X PATCH https://localhost:9443/api/users/john.doe \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "roles": {
      "values": ["admin", "api-developer"]
    }
  }'
```

## 🔌 LDAP Integration

### Enable LDAP in .env

```env
LDAP_ENABLED=true
LDAP_URL=ldap://ldap-server:389
LDAP_DN=cn=admin,dc=example,dc=com
LDAP_PASSWORD=your_ldap_password
```

### Configure LDAP in Admin Console

1. Navigate to: Main → User Management → User Stores
2. Add LDAP User Store
3. Configure LDAP connection details
4. Test connection

## 📧 Email Configuration

### Setup Email for Password Recovery

Edit `.env`:
```env
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=noreply@example.com
SMTP_PASSWORD=app_specific_password
SMTP_FROM=noreply@example.com
```

## 🧪 Testing

### Test OAuth2 Flow

```bash
# 1. Get Client Credentials
CLIENT_ID="your-client-id"
CLIENT_SECRET="your-client-secret"

# 2. Get Access Token
TOKEN=$(curl -s -X POST https://localhost:9443/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET&scope=api" \
  | jq -r '.access_token')

# 3. Use Token
curl -X GET https://localhost:9443/api/me \
  -H "Authorization: Bearer $TOKEN"
```

### Test User Authentication

```bash
# Get user info
curl -X GET https://localhost:9443/api/users/admin \
  -H "Authorization: Bearer $TOKEN"
```

## 📊 Monitoring

### View Logs

```bash
# Tail logs
docker compose logs cms-wso2is -f

# View specific error logs
docker compose logs cms-wso2is | grep ERROR
```

### Health Check

```bash
# Check service health
curl -k https://localhost:9443/api/identity/auth/v1.0/token

# Check database connection
docker compose exec cms-wso2is pg_isready -h cms-postgresql
```

### Performance Metrics

Access from Admin Console:
- Main → Monitor → Statistics
- View active users, sessions, API calls
- Monitor token generation rates

## 🔒 Security Best Practices

### Production Checklist

- [ ] Change admin password
- [ ] Configure SSL/TLS certificates
- [ ] Enable MFA for admin accounts
- [ ] Set up audit logging
- [ ] Configure secure session timeout
- [ ] Enable CORS restrictions
- [ ] Set up backup strategy
- [ ] Monitor access logs
- [ ] Use HTTPS everywhere
- [ ] Implement rate limiting

### SSL/TLS Certificate

1. Generate self-signed cert (dev):
```bash
keytool -genkey -alias wso2is -keyalg RSA -keysize 2048 \
  -keystore wso2carbon.jks -validity 365
```

2. For production, use proper CA certificates

## 🐛 Troubleshooting

### Issue: Cannot access admin console

**Solution:**
1. Check if container is running: `docker compose ps cms-wso2is`
2. Check logs: `docker compose logs cms-wso2is --tail 50`
3. Wait for startup (takes 1-2 minutes)
4. Accept SSL certificate warning in browser

### Issue: Database connection error

**Solution:**
1. Verify PostgreSQL is running: `docker compose ps cms-postgresql`
2. Check database exists: `createdb -U postgres -h localhost wso2is`
3. Verify credentials in `.env`
4. Check logs: `docker compose logs cms-wso2is`

### Issue: OAuth2 token request fails

**Solution:**
1. Verify Client ID & Secret are correct
2. Check OAuth2 scopes configuration
3. Verify redirect URI is registered
4. Check token endpoint URL is correct

### Issue: User cannot login

**Solution:**
1. Verify user account exists
2. Check if user is active
3. Verify password is correct
4. Check role assignments
5. Review audit logs in Admin Console

## 📚 API Reference

### Authentication
```
POST /oauth2/token - Get access token
POST /oauth2/authorize - Authorization endpoint
POST /oauth2/revoke - Revoke token
```

### Users
```
GET /api/users - List users
POST /api/users - Create user
GET /api/users/{userId} - Get user
PATCH /api/users/{userId} - Update user
DELETE /api/users/{userId} - Delete user
```

### Applications
```
GET /api/applications - List applications
POST /api/applications - Create application
GET /api/applications/{appId} - Get application
PATCH /api/applications/{appId} - Update application
DELETE /api/applications/{appId} - Delete application
```

### Roles
```
GET /api/roles - List roles
POST /api/roles - Create role
PATCH /api/roles/{roleId} - Update role
DELETE /api/roles/{roleId} - Delete role
```

## 📖 Additional Resources

- [WSO2 IS Documentation](https://is.docs.wso2.com/en/7.0.0/)
- [OAuth2 & OIDC Guide](https://is.docs.wso2.com/en/7.0.0/reference/grant-types/)
- [REST API Reference](https://is.docs.wso2.com/en/7.0.0/reference/REST-API/)
- [User Store Management](https://is.docs.wso2.com/en/7.0.0/learn/managing-users-and-roles/)
- [Security Best Practices](https://is.docs.wso2.com/en/7.0.0/learn/security-guidelines/)

## 🤝 Integration with CMS Platform

### Integrate with Frontend

In frontend auth configuration:
```javascript
const oauth2Config = {
  clientId: 'your-client-id',
  clientSecret: 'your-client-secret',
  authorizationEndpoint: 'https://localhost:9443/oauth2/authorize',
  tokenEndpoint: 'https://localhost:9443/oauth2/token',
  userInfoEndpoint: 'https://localhost:9443/oauth2/userinfo',
  redirectUri: 'http://localhost:3000/callback',
  scopes: ['openid', 'profile', 'email', 'api']
};
```

### Protect Backend APIs

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    # Verify JWT token from WSO2 IS
    # Extract claims and validate
    return token_claims
```

## 📝 Maintenance

### Backup Database

```bash
docker compose exec cms-postgresql pg_dump -U postgres wso2is > wso2is_backup.sql
```

### Restore Database

```bash
cat wso2is_backup.sql | docker compose exec -T cms-postgresql psql -U postgres wso2is
```

### Update WSO2 IS

1. Stop current service: `docker compose down`
2. Update version in docker-compose.yml
3. Restart: `docker compose up -d cms-wso2is`

---

**Last Updated:** April 2026
**Version:** WSO2 IS 7.0.0
**Status:** Production Ready
