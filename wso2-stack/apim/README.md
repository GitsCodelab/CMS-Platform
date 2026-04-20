# WSO2 API Manager (APIM) Setup

This directory contains the configuration for WSO2 API Manager integration with the CMS Platform.

## Overview

WSO2 API Manager is an enterprise-grade API management platform that provides:
- **API Gateway**: Enforce policies, throttling, and security
- **Publisher Portal**: Create, manage, and publish APIs
- **Developer Portal**: Allows developers to discover and subscribe to APIs
- **Admin Portal**: System administration and configuration

## 🚀 Quick Start - First Time Setup

### ⚡ AUTOMATIC SETUP (RECOMMENDED - 1 Command)

This is the easiest way to set up WSO2 APIM - Docker Compose handles everything:

```bash
# From repository root directory
cd /path/to/CMS-Platform

# Start all services (builds image, initializes DB, starts APIM)
docker compose up -d

# Verify APIM is running
docker ps | grep cms-apim

# Check initialization status
docker logs cms-apim | tail -50
```

**What happens automatically:**
✅ PostgreSQL starts first  
✅ WSO2 APIM image is built from Dockerfile  
✅ Database is created and initialized  
✅ APIM starts on ports 8280, 8243, 9443, 9611  
✅ All configurations are applied  
✅ Container becomes healthy in ~2-5 minutes  

---

### 🔧 MANUAL SETUP (Step-by-Step)

If you prefer more control or Docker Compose isn't available:

#### Step 1: Start PostgreSQL First

```bash
cd /path/to/CMS-Platform
docker compose up cms-postgresql -d
sleep 10
docker ps | grep postgresql
```

#### Step 2: Create WSO2 Database

```bash
docker exec cms-postgresql psql -U postgres -c "CREATE DATABASE wso2am;"
```

#### Step 3: Build WSO2 APIM Image

```bash
docker compose build --no-cache cms-apim
```

#### Step 4: Start APIM Service

```bash
docker compose up cms-apim -d
sleep 60  # Wait for full initialization
```

#### Step 5: Verify Service is Healthy

```bash
# Check container is running
docker ps | grep cms-apim

# Verify service is ready
docker logs cms-apim | grep "Started"

# Check health status
docker inspect --format='{{.State.Health.Status}}' cms-apim
```

#### Step 6: Restart for Final Initialization (Optional but Recommended)

```bash
docker restart cms-apim
sleep 30
```

---

### 🤖 FULLY AUTOMATED SETUP SCRIPT

Create a file called `setup-wso2.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 WSO2 APIM Automated Setup"
echo "======================================"

cd /path/to/CMS-Platform

# Step 1: Build
echo "📦 Building WSO2 APIM image..."
docker compose build --no-cache cms-apim

# Step 2: Start PostgreSQL
echo "🐳 Starting PostgreSQL..."
docker compose up cms-postgresql -d
sleep 10

# Step 3: Create database
echo "🗄️  Creating WSO2 database..."
docker exec cms-postgresql psql -U postgres -c "CREATE DATABASE wso2am;" 2>/dev/null || echo "✓ DB already exists"

# Step 4: Start APIM
echo "🚀 Starting WSO2 APIM..."
docker compose up cms-apim -d
sleep 60

# Step 5: Verify
echo ""
echo "✅ Verification:"
docker ps | grep -E "(postgresql|apim)" || echo "⚠️  Containers not found"

echo ""
echo "======================================"
echo "✅ WSO2 APIM Setup Complete!"
echo "======================================"
echo ""
echo "🔐 Access Points:"
echo "   Admin Console: https://localhost:9443/admin"
echo "   Publisher: https://localhost:9443/publisher"
echo "   Developer Portal: https://localhost:9443/devportal"
echo "   API Gateway (HTTP): http://localhost:8280"
echo "   API Gateway (HTTPS): https://localhost:8243"
echo ""
echo "🔑 Default Credentials:"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "⏱️  Note: First startup takes 2-5 minutes. Check logs: docker logs -f cms-apim"
```

Run it:
```bash
chmod +x setup-wso2.sh
bash setup-wso2.sh
```

---

### ✅ First-Run Verification Checklist

After setup is complete, verify everything:

```bash
# 1. Check containers are running
docker ps | grep -E "postgresql|apim"
# Should show: cms-postgresql and cms-apim as "Up"

# 2. Check APIM is initialized
docker logs cms-apim | tail -20
# Should show: "Started WSO2 API Manager"

# 3. Check database connection
docker exec cms-apim curl -s https://localhost:9443/api/am/admin/v0.17/system-info -k | head -20
# Should return JSON response (not connection error)

# 4. Verify database exists
docker exec cms-postgresql psql -U postgres -l | grep wso2am
# Should show: wso2am database

# 5. Test API Gateway port
curl -v http://localhost:8280/
# Should respond (not connection refused)

# 6. Test APIM console (with valid SSL warning)
curl -k https://localhost:9443/admin
# Should return HTML (not connection error)
```

---

### 🌐 Access WSO2 APIM Portals

| Portal | URL | Username | Password | Purpose |
|--------|-----|----------|----------|---------|
| **Admin Console** | https://localhost:9443/admin | admin | admin | System settings & user management |
| **Publisher** | https://localhost:9443/publisher | admin | admin | Create & publish APIs |
| **Developer Portal** | https://localhost:9443/devportal | - | - | Discover & subscribe to APIs |
| **API Gateway (HTTP)** | http://localhost:8280 | - | - | Route API traffic (unencrypted) |
| **API Gateway (HTTPS)** | https://localhost:8243 | - | - | Route API traffic (encrypted) |
| **Analytics** | http://localhost:9611 | admin | admin | Analytics dashboard (optional) |

**Note**: The first login may take 1-2 minutes as the system initializes. If you get connection errors, wait a bit and retry.

---

### ⚠️ TROUBLESHOOTING First-Run Issues

**Container won't start:**
```bash
# View detailed error logs
docker logs cms-apim

# Check if port is already in use
lsof -i :9443
lsof -i :8280
lsof -i :8243

# If ports in use, stop conflicting containers and rebuild
docker compose down
docker compose up -d
```

**Database connection error:**
```bash
# Verify PostgreSQL is running
docker ps | grep postgresql

# Check database was created
docker exec cms-postgresql psql -U postgres -l | grep wso2am

# Recreate database if needed
docker exec cms-postgresql psql -U postgres -c "DROP DATABASE IF EXISTS wso2am;"
docker exec cms-postgresql psql -U postgres -c "CREATE DATABASE wso2am;"
```

**Portal returns 500 error:**
```bash
# Wait longer for startup (can take 5+ minutes on first run)
docker logs cms-apim -f
# Wait for "Started WSO2 API Manager" message

# Restart if still hanging
docker restart cms-apim
sleep 30
```

**Can't access https://localhost:9443:**
```bash
# Check if service is listening
docker exec cms-apim netstat -tlnp | grep 9443

# Try with curl
curl -k https://localhost:9443/admin

# Verify health status
docker inspect --format='{{.State.Health}}' cms-apim
```

---

### 📊 Expected First-Run Timeline

| Time | Event |
|------|-------|
| 0-5s | Container starts, Java initializes |
| 5-30s | Database connection established |
| 30-60s | Initial services load |
| 60-120s | Full startup complete, portals accessible |
| 120-300s | Full optimization, all services ready |

**First startup may be slow - this is normal!**

---

### 🔑 API Gateway Endpoints

Once running, API traffic routes through:

```
Your Client
    ↓
https://localhost:9443 (Admin/Publisher)
http://localhost:8280 (API Gateway HTTP)
https://localhost:8243 (API Gateway HTTPS)
    ↓
CMS Backend (cms-backend:8000)
    ↓
Oracle/PostgreSQL Databases
```

## Configuration

### Environment Variables (in docker-compose.yml)

```yaml
DB_TYPE: postgresql              # Database type
DB_HOSTNAME: cms-postgresql      # PostgreSQL host
DB_PORT: 5432                    # PostgreSQL port
DB_NAME: wso2am                  # Database name
DB_USERNAME: postgres            # DB user
DB_PASSWORD: postgres            # DB password
ADMIN_USERNAME: admin            # APIM admin user
ADMIN_PASSWORD: admin            # APIM admin password
API_GATEWAY_HOST: cms-apim       # Gateway hostname
API_GATEWAY_HTTP_PORT: 8280      # Gateway HTTP port
API_GATEWAY_HTTPS_PORT: 8243     # Gateway HTTPS port
```

### Ports Exposed

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Admin/Publisher | 9443 | HTTPS | Administrative console |
| API Gateway | 8280 | HTTP | API Gateway (unencrypted) |
| API Gateway | 8243 | HTTPS | API Gateway (encrypted) |
| Analytics | 9611 | TCP | Optional analytics engine |

## Registering Your CMS Platform APIs

### Step 1: Create an API

1. Access Publisher Portal: https://localhost:9443/publisher
2. Click **Create** → **Create New API**
3. Select **REST API**
4. Fill in details:
   - **Name**: `CMS Oracle API`
   - **Context**: `/cms/oracle`
   - **Version**: `1.0.0`
   - **Backend**: `http://cms-backend:8000/oracle` (Docker network URL)
5. Save & Publish

### Step 2: Register Gateway Endpoints

Add the following endpoints to route CMS API traffic:
- Oracle API: `http://cms-backend:8000/oracle`
- PostgreSQL API: `http://cms-backend:8000/postgres`

### Step 3: Apply Policies

In WSO2 APIM, apply these common policies:
- **Throttling**: Limit API calls per time period
- **Authentication**: Require OAuth2 tokens
- **CORS**: Allow cross-origin requests
- **Rate Limiting**: Prevent abuse

## Docker Network Integration

WSO2 APIM connects to the CMS Platform via the `cms-platform-net` bridge network:
- PostgreSQL: `cms-postgresql:5432`
- Backend: `cms-backend:8000`
- Frontend: `cms-frontend:3000`
- Oracle: `cms-oracle-xe:1521`

## Health Check

The service includes a health check that:
- Polls the APIM system info endpoint every 30 seconds
- Waits up to 120 seconds for startup
- Requires 5 consecutive successes for "healthy" status

Check health:
```bash
docker inspect --format='{{.State.Health.Status}}' cms-apim
```

## Database Information

The `wso2am` PostgreSQL database stores:
- User and role management data
- API definitions and metadata
- Subscription and throttling information
- Analytics data

To verify database exists:
```bash
docker exec cms-postgresql psql -U postgres -l | grep wso2am
```

To backup the database:
```bash
docker exec cms-postgresql pg_dump -U postgres wso2am > wso2am-backup.sql
```

To restore from backup:
```bash
docker exec -i cms-postgresql psql -U postgres -d wso2am < wso2am-backup.sql
```

## Volumes

- **wso2am-data**: Persists configuration and data files
- **wso2am-logs**: Persists application logs

Stored in Docker volumes at: `/var/lib/docker/volumes/`

## Logs

View WSO2 APIM logs:
```bash
docker logs -f cms-apim
```

Or access logs from within the container:
```bash
docker exec cms-apim tail -f /home/wso2carbon/wso2am-4.1.0/repository/logs/wso2carbon.log
```

## Integration with CMS Platform APIs

### Example: Creating an API for Oracle CRUD

1. **In WSO2 Publisher**:
   - Name: `CMS Test Table API`
   - Backend URL: `http://cms-backend:8000/oracle/test`
   - Methods: GET, POST, PUT, DELETE

2. **In CMS Frontend**:
   - Add middleware to inject APIM access tokens
   - Route API calls through gateway: `https://localhost:8243/cms/test`

3. **Apply Policies**:
   - OAuth2 authentication
   - API key validation
   - Request/response transformation

## Troubleshooting

### Database does not exist error (FATAL: database "wso2am" does not exist)
This occurs on first startup if the database hasn't been initialized.

**Solution**:
```bash
# 1. Create the database
docker exec cms-postgresql psql -U postgres -c "CREATE DATABASE wso2am;"

# 2. Initialize schemas
docker exec cms-apim cat /home/wso2carbon/wso2am-4.3.0/dbscripts/postgresql.sql > /tmp/wso2-init.sql
docker exec -i cms-postgresql psql -U postgres -d wso2am < /tmp/wso2-init.sql

docker exec cms-apim cat /home/wso2carbon/wso2am-4.3.0/dbscripts/apimgt/postgresql.sql > /tmp/wso2-apimgt.sql
docker exec -i cms-postgresql psql -U postgres -d wso2am < /tmp/wso2-apimgt.sql

# 3. Restart APIM
docker restart cms-apim
```

### Service won't start
- Check PostgreSQL is running: `docker compose up cms-postgresql`
- Wait 2-3 minutes for database initialization
- Check logs: `docker logs cms-apim`

### Connection refused on port 9443
- APIM startup takes 2-3 minutes after database initialization
- Check health: `docker inspect --format='{{.State.Health.Status}}' cms-apim`
- Ensure certificate is accepted (self-signed)

### Database connection error
- Verify PostgreSQL credentials match deployment.toml
- Ensure PostgreSQL container is running: `docker ps | grep cms-postgresql`
- Check network connectivity: `docker network inspect cms-platform-net`
- Verify database exists: `docker exec cms-postgresql psql -U postgres -l | grep wso2am`

### Can't access internal services
- Verify Docker network: `docker network inspect cms-platform-net`
- Check service hostnames: `docker inspect cms-backend | grep IPAddress`

## Production Considerations

1. **Use Official Certificates**: Replace self-signed certs with proper SSL/TLS
2. **Change Default Credentials**: Update admin/admin password
3. **Enable Database Backups**: Setup PostgreSQL backup schedule
4. **Use API Keys**: Enforce API key validation for all endpoints
5. **Enable Analytics**: Set `ANALYTICS_ENABLED: true` for production monitoring
6. **Resource Limits**: Add CPU/memory limits in docker-compose.yml
7. **Reverse Proxy**: Use nginx to expose APIM behind corporate proxy

## Additional Resources

- [WSO2 API Manager Documentation](https://apim.docs.wso2.com/)
- [WSO2 Docker Hub](https://hub.docker.com/r/wso2/wso2am)
- [API Manager 4.1.0 Release Notes](https://apim.docs.wso2.com/en/4.1.0/)
- [Policy Management Guide](https://apim.docs.wso2.com/en/4.1.0/design/policies/overview/)

## Contributing

To modify WSO2 APIM configuration:
1. Update environment variables in `docker-compose.yml`
2. Rebuild if needed: `docker compose build --no-cache cms-apim`
3. Restart service: `docker compose restart cms-apim`
