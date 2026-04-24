# CMS Platform - New Server Setup Guide

Complete guide to set up the CMS Platform on a fresh server environment.

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended), macOS, or WSL2 on Windows
- **CPU**: 4+ cores
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 50GB free space (including Docker images and volumes)
- **Network**: Outbound internet access for Docker image pulls

### Required Software

#### 1. Docker & Docker Compose
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose-plugin

# Verify installation
docker --version
docker compose version

# Add current user to docker group (no sudo needed)
sudo usermod -aG docker $USER
# Logout and login for changes to take effect
```

#### 2. Git
```bash
sudo apt install -y git
git --version
```

#### 3. Node.js (Optional, for local frontend development)
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
node --version
npm --version
```

#### 4. Python 3.12 (Optional, for local backend development)
```bash
sudo apt install -y python3.12 python3.12-venv python3.12-dev
python3.12 --version
```

## Step-by-Step Installation

### 1. Clone Repository

```bash
# Navigate to desired directory
cd ~/projects  # or your preferred location

# Clone CMS Platform repository
git clone https://github.com/yourusername/CMS-Platform.git
cd CMS-Platform

# Verify directory structure
ls -la
```

### 2. Verify Docker Installation

```bash
# Start Docker service (if not running)
sudo systemctl start docker
sudo systemctl enable docker  # Auto-start on reboot

# Verify Docker is running
docker ps

# Verify Docker Compose
docker compose --version
```

### 3. Configure Environment Files

```bash
# Backend environment
cat > backend/.env << 'EOF'
# Oracle Configuration
ORACLE_HOST=cms-oracle-xe
ORACLE_PORT=1521
ORACLE_USER=system
ORACLE_PASSWORD=oracle
ORACLE_SERVICE=xepdb1

# PostgreSQL Configuration
POSTGRES_HOST=jposee-db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=jposee

# API Configuration
API_TITLE=CMS Platform API
API_VERSION=1.0.0
EOF

# Airflow environment
cat > airflow/.env << 'EOF'
# Airflow Settings
AIRFLOW_UID=50000
AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://postgres:postgres@cms-postgresql:5432/cms
AIRFLOW__CORE__FERNET_KEY=your-fernet-key-here
EOF
```

### 4. Start Docker Services

```bash
# Pull all images (may take 5-10 minutes on first run)
docker compose pull

# Start all services in background
docker compose up -d

# Verify all containers are running
docker compose ps

# Expected output shows all services "Up" with health status
```

### 5. Initialize Databases

```bash
# Wait 30 seconds for services to fully initialize
sleep 30

# Run jposee-db schema migration
cat backend/migrations/001_create_jposee_schema.sql | \
  docker exec -i jposee-db psql -U postgres -d jposee

# Verify schema creation
docker exec jposee-db psql -U postgres -d jposee -c "\dt"
```

### 6. Verify Installation

```bash
# Check all services
docker compose ps

# Test Backend API
curl http://localhost:8000/jposee/monitoring/health | jq .

# Test Frontend accessibility
curl -I http://localhost:3000

# Test Airflow
curl http://localhost:8080/health | jq .

# Test WSO2 APIM
curl -k https://localhost:9443/api/am/admin/v0.17/system-info | jq .
```

### 7. Access Web Interfaces

Open in browser:
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Airflow**: http://localhost:8080 (airflow / airflow)
- **WSO2 APIM Admin**: https://localhost:9443/admin (admin / admin)
- **jPOS**: localhost:5000 (ISO 8583)
- **jPOS EE**: localhost:5001 (ISO 8583)

## Architecture Overview

### Dedicated Database Approach (Current)

```
┌─────────────────────────────────────────┐
│     Docker Container Network            │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐   ┌──────────────┐  │
│  │  cms-db      │   │  jposee-db   │  │
│  │  (cms data)  │   │  (payments)  │  │
│  │  Port 5432   │   │  Port 5433   │  │
│  └──────┬───────┘   └──────┬───────┘  │
│         │                  │          │
│  ┌──────▼──────────────────▼────────┐ │
│  │  cms-backend (FastAPI)           │ │
│  │  ├─ /jposee/* endpoints          │ │
│  │  ├─ Transaction CRUD             │ │
│  │  └─ Routing operations           │ │
│  │  Port 8000                       │ │
│  └──────┬──────────────┬────────────┘ │
│         │              │              │
│  ┌──────▼────┐  ┌─────▼──────┐      │
│  │ Frontend  │  │ jPOS/APIM  │      │
│  │ (React)   │  │ (Gateway)  │      │
│  │ 3000      │  │ 9443/8280  │      │
│  └───────────┘  └────────────┘      │
│                                         │
└─────────────────────────────────────────┘
```

### Database Separation Benefits

- **Performance**: Isolated I/O for payments vs. platform data
- **Scaling**: Independent database sizing
- **Backup**: Separate backup strategies per database
- **Security**: Different access controls and encryption
- **High Availability**: Can be deployed on separate hosts

## Troubleshooting

### Services Won't Start

```bash
# View error logs
docker compose logs cms-backend
docker compose logs jposee-db

# Restart a failed service
docker compose restart cms-backend

# Full restart
docker compose down
docker compose up -d
```

### Database Connection Errors

```bash
# Verify jposee-db is healthy
docker compose ps jposee-db
# Should show "healthy" status

# Test connection directly
docker exec jposee-db psql -U postgres -d jposee -c "SELECT version();"

# Check backend config
docker exec cms-backend env | grep POSTGRES
```

### Port Already in Use

```bash
# Find process using port (e.g., 8000)
sudo lsof -i :8000

# Change port in docker-compose.yml and restart
# Example: Change "8000:8000" to "8001:8000"
docker compose down
docker compose up -d
```

### Low Disk Space

```bash
# Clean up unused Docker resources
docker system prune -a

# Remove old container volumes
docker volume prune

# Check disk usage
docker system df
```

## Production Readiness Checklist

Before moving to production, ensure:

- [ ] All containers running and healthy
- [ ] Database backups configured
- [ ] SSL/TLS certificates installed
- [ ] Firewall rules configured
- [ ] Monitoring and alerting enabled
- [ ] Log aggregation configured
- [ ] Rate limiting configured
- [ ] Security scanning completed
- [ ] Load testing passed
- [ ] Disaster recovery plan tested

See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for detailed production setup.

## Performance Tuning

### Docker Daemon Settings

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65536,
      "Soft": 65536
    }
  }
}
```

### PostgreSQL Optimization

```bash
# Connect to jposee-db
docker exec -it jposee-db psql -U postgres -d jposee

# Check current settings
SHOW shared_buffers;
SHOW work_mem;
SHOW maintenance_work_mem;

# These can be adjusted in docker-compose.yml environment variables
```

## Maintenance Commands

```bash
# View service logs
docker compose logs -f [service-name]

# Check disk usage
docker exec jposee-db du -h /var/lib/postgresql/data/

# Backup jposee database
docker exec jposee-db pg_dump -U postgres jposee > backup_jposee.sql

# Restore jposee database
docker exec -i jposee-db psql -U postgres < backup_jposee.sql

# Update images
docker compose pull
docker compose up -d

# Full system restart
docker compose restart
```

## Getting Help

- Check [README.md](README.md) for architecture overview
- Review [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for production setup
- Check individual service logs for detailed errors
- Verify all prerequisites are installed correctly

## Next Steps

1. ✅ Follow this guide to set up development environment
2. ✅ Run API tests to verify functionality
3. ✅ Configure for production (see PRODUCTION_DEPLOYMENT.md)
4. ✅ Deploy to production servers
5. ✅ Monitor and maintain

---

**Last Updated**: April 21, 2026  
**Platform Version**: 1.0.0  
**Docker Compose Version**: 2.17.0+
