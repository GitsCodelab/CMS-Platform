# WSO2 API Manager - First Time Setup Guide

## Overview

This guide provides step-by-step instructions for setting up WSO2 API Manager (v4.3.0) with PostgreSQL database integration in a Docker environment. This setup includes proper health checks and service dependencies to ensure all services start in the correct order.

## Prerequisites

- Docker and Docker Compose installed
- Git repository cloned
- Basic understanding of Docker and Docker Compose

## Key Configuration Changes

### 1. PostgreSQL Health Check
A health check has been added to PostgreSQL to ensure the database is ready before dependent services attempt to connect.

**Configuration:**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -d cms"]
  interval: 5s
  timeout: 5s
  retries: 20
  start_period: 10s
```

**Why:** PostgreSQL needs time to complete recovery/initialization. Without this, APIM tries to connect too early and fails with "FATAL: database system is not yet accepting connections".

### 2. Service Dependency Conditions
All services that depend on PostgreSQL now wait for `service_healthy` instead of just `service_started`.

**Configuration:**
```yaml
depends_on:
  cms-postgresql:
    condition: service_healthy
```

**Why:** This ensures dependent services only start when PostgreSQL is actually ready to accept connections, not just when the container has started.

## Setup Commands Reference

Follow these commands in sequence to set up and run the CMS Platform with WSO2 APIM:

| Seq | Command | Purpose | Expected Output |
|-----|---------|---------|-----------------|
| 1 | `cd /home/user/cms-platform/CMS-Platform` | Navigate to project root | Terminal shows current directory |
| 2 | `git status` | Check for uncommitted changes | Lists modified files |
| 3 | `git add .` | Stage all changes | No output (success) |
| 4 | `git commit -m "Setup WSO2 APIM with healthcheck and service dependencies"` | Commit changes | Shows commit hash and changes |
| 5 | `git push origin dev-maf` | Push to remote repository | Shows remote branch update |
| 6 | `docker compose down` | Stop and remove all containers | Shows removal of containers (~60s) |
| 7 | `docker compose up -d` | Start all services in background | Shows service creation (~120s) |
| 8 | `docker ps --format "table {{.Names}}\t{{.Status}}"` | Check container status | Lists all 8 containers with status |
| 9 | `docker logs cms-postgresql \| tail -20` | Verify PostgreSQL is ready | Shows "database system is ready to accept connections" |
| 10 | `docker logs cms-apim \| tail -50` | Verify APIM started successfully | Shows deployment logs without "FATAL" errors |
| 11 | `docker logs cms-apim \| grep -i -E "(error\|fatal\|exception\|ready)" \| tail -20` | Check for critical errors | Should show "Server ready for processing..." |

## Access Information

### WSO2 APIM Publisher

**HTTPS (Recommended):**
- URL: `https://localhost:9443/publisher`
- Port: 9443 (HTTPS)
- Note: Accept self-signed certificate warning in development environment

**HTTP (Alternative):**
- URL: `http://localhost:8280/publisher`
- Port: 8280 (HTTP Gateway)

**Default Credentials:**
- Username: `admin`
- Password: `admin`

### Other Important Ports

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Publisher | 9443 | HTTPS | API Publisher interface |
| Publisher | 8280 | HTTP | API Gateway (HTTP) |
| Admin | 9443 | HTTPS | Admin services |
| Admin | 8280 | HTTP | HTTP Gateway |
| PostgreSQL | 5432 | TCP | Database |
| Backend API | 8000 | HTTP | Python backend service |

## Troubleshooting

### APIM Fails to Connect to PostgreSQL
**Error:** `FATAL: the database system is not yet accepting connections`

**Solution:** This typically means PostgreSQL is still initializing. The health check should prevent this, but if it occurs:
1. Wait 2-3 minutes for PostgreSQL to complete recovery
2. Check PostgreSQL logs: `docker logs cms-postgresql`
3. Verify health check status: `docker ps` (should show "Healthy")

### Port 9443 Requires TLS
**Error:** `Bad Request - This combination of host and port requires TLS.`

**Solution:** Use HTTPS instead of HTTP:
- Change `http://localhost:9443/publisher` to `https://localhost:9443/publisher`

### Services Stuck in "Creating" State
**Solution:**
1. Force stop all services: `docker compose down -v`
2. Remove dangling containers: `docker system prune -f`
3. Start fresh: `docker compose up -d`

## Files Modified

| File | Change | Reason |
|------|--------|--------|
| `docker-compose.yml` | Added PostgreSQL healthcheck and service_healthy conditions | Ensure proper startup ordering |
| `wso2-stack/apim/docker-compose.yml` | Updated APIM dependency to service_healthy | Prevent premature APIM startup |

## Environment Information

- **WSO2 API Manager Version:** 4.3.0
- **PostgreSQL Version:** 15.3
- **Java Version:** 17.0.11
- **Docker Compose Version:** 3.x+
- **Host OS:** Linux

## Quick Start for New Users

For first-time setup on a new PC:

```bash
# 1. Clone or update repository
cd /home/user/cms-platform/CMS-Platform

# 2. Ensure clean slate
docker compose down -v

# 3. Start all services
docker compose up -d

# 4. Wait for PostgreSQL to become healthy (~2 minutes)
watch docker ps  # Press Ctrl+C when cms-postgresql shows "Healthy"

# 5. Verify APIM is ready
docker logs cms-apim | grep -i "Server ready"

# 6. Access WSO2 APIM Publisher
# Open in browser: https://localhost:9443/publisher
# Default credentials: admin / admin
```

## Verification Checklist

After running `docker compose up -d`, verify:

- [ ] PostgreSQL container status is "Healthy" (wait ~2 minutes)
- [ ] All 8 containers are in "Up" or "Running" state
- [ ] No "FATAL" errors in APIM logs
- [ ] APIM logs show "Server ready for processing..."
- [ ] Can access https://localhost:9443/publisher without connection errors
- [ ] Can log in with admin/admin credentials

## Support

For issues or questions, check:
1. Docker container logs: `docker logs <container_name>`
2. This setup guide
3. WSO2 APIM documentation: https://apim.docs.wso2.com/en/latest/

---
**Last Updated:** April 20, 2026
**Setup Verified On:** Ubuntu Linux with Docker 24.x and Docker Compose 2.x
