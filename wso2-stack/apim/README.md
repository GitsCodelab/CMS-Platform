# WSO2 API Manager (APIM) Setup

This directory contains the configuration for WSO2 API Manager integration with the CMS Platform.

## Overview

WSO2 API Manager is an enterprise-grade API management platform that provides:
- **API Gateway**: Enforce policies, throttling, and security
- **Publisher Portal**: Create, manage, and publish APIs
- **Developer Portal**: Allows developers to discover and subscribe to APIs
- **Admin Portal**: System administration and configuration

## Quick Start

### Start WSO2 APIM with Docker Compose

From the root directory:
```bash
docker compose up cms-apim
```

This will:
1. Pull the official WSO2 API Manager image (wso2/wso2am:4.1.0)
2. Initialize the PostgreSQL database connection (wso2am_db)
3. Start the API Manager on the configured ports

### Access WSO2 APIM

**Admin Console (Publisher & Admin Portal)**
- URL: https://localhost:9443/admin
- Username: `admin`
- Password: `admin`
- Note: Accept the self-signed certificate

**Publisher Portal (Create/Publish APIs)**
- URL: https://localhost:9443/publisher
- Username: `admin`
- Password: `admin`

**Developer Portal (API Discovery)**
- URL: https://localhost:9443/devportal
- Public API discovery and subscription

**API Gateway Endpoints**
- HTTP: `http://localhost:8280`
- HTTPS: `http://localhost:8243`

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

## Database Setup

The PostgreSQL container will automatically create the `wso2am_db` database if it doesn't exist. First-time initialization may take 2-3 minutes.

To manually check the database:
```bash
docker exec cms-postgresql psql -U postgres -l | grep wso2am
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

### Service won't start
- Check PostgreSQL is running: `docker compose up cms-postgresql`
- Wait 2-3 minutes for database initialization
- Check logs: `docker logs cms-apim`

### Connection refused on port 9443
- APIM startup takes 2-3 minutes
- Check health: `docker healthcheck inspect cms-apim`
- Ensure certificate is accepted (self-signed)

### Database connection error
- Verify PostgreSQL credentials match (.env file)
- Ensure PostgreSQL container is running
- Check network connectivity: `docker network inspect cms-platform-net`

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
