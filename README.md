# CMS Platform

A comprehensive, enterprise-grade content management system featuring:
- **Dual-Database Support**: Oracle XE (transactional) and PostgreSQL (data warehouse)
- **Modern Frontend**: React 18.2.0 with Vite, SAP Fiori Design System, OpenUI5 components, and pagination
- **Robust Backend**: FastAPI with comprehensive REST API and database abstraction
- **Workflow Orchestration**: Apache Airflow 3.0.0 for ETL pipelines and scheduling
- **API Management**: WSO2 APIM 4.1.0 for API lifecycle management and gateway
- **Complete Container Orchestration**: Docker Compose with fully integrated microservices
- **Production-Ready**: Health checks, monitoring, logging, and error handling
- **Enterprise UI**: SAP Horizon theme with 106+ test records, pagination, and professional styling

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.12+ (for local backend development)
- Linux/WSL2 environment recommended

### Startup with Docker Compose

```bash
# Start all services in background
docker compose up -d

# View logs (optional)
docker compose logs -f

# Verify all containers are running
docker compose ps

# Stop all services
docker compose down
```

📖 See [SETUP_NEW_SERVER.md](SETUP_NEW_SERVER.md) for complete new server setup  
📖 See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for production environment guide

### Access Points

| Service | URL | Default Credentials | Port(s) |
|---------|-----|-------------------|---------|
| **Frontend (React)** | http://localhost:3000 | - | 3000 |
| **Backend API** | http://localhost:8000 | - | 8000 |
| **Backend API Docs** | http://localhost:8000/docs | - | 8000 |
| **Airflow UI** | http://localhost:8080 | airflow / airflow | 8080 |
| **WSO2 APIM Admin** | https://localhost:9443/admin | admin / admin | 9443 |
| **WSO2 APIM Publisher** | https://localhost:9443/publisher | admin / admin | 9443 |
| **WSO2 APIM Developer** | https://localhost:9443/devportal | - | 9443 |
| **APIM Gateway (HTTP)** | http://localhost:8280 | - | 8280 |
| **APIM Gateway (HTTPS)** | https://localhost:8243 | - | 8243 |
| **Oracle Database** | localhost:1521/xepdb1 | sys / oracle | 1521 |
| **PostgreSQL (CMS)** | localhost:5432/cms | postgres / postgres | 5432 |

---

## 📐 Architecture Overview

### Full Service Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           CMS PLATFORM                                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│                      ┌──────────────────┐                                │
│                      │  Frontend        │                                │
│                      │  (React)         │                                │
│                      │  Port 3000       │                                │
│                      └────────┬─────────┘                                │
│                               │                                          │
│                      ┌────────▼────────────┐                            │
│                      │   WSO2 APIM         │                            │
│                      │  (API Gateway)      │                            │
│                      │  Port 9443/8280     │                            │
│                      │    /8243            │                            │
│                      └────┬───┬────┬───────┘                            │
│           ┌────────────────┘   │    └──────────────┐                   │
│           │                    │                                          │
│    ┌──────▼──────┐             │                                          │
│    │  Backend    │             │                                          │
│    │ (FastAPI)   │             │                                          │
│    │ Port 8000   │             │                                          │
│    └──────┬──────┘             │                                          │
│           │                    │                                          │
│    ┌──────▼─────────────────┐                                         │
│    │   Supporting Services  │                                         │
│    ├────────────────────────┤                                         │
│    │ • Databases            │                                         │
│    │   ├─ Oracle XE (1521)  │                                         │
│    │   └─ PostgreSQL (5432) │                                         │
│    │ • Airflow (Port 8080)  │                                         │
│    │   Scheduler & Workflow │                                         │
│    └────────────────────────┘                                         │
│                                                                            │
│        🔗 Docker Bridge Network: cms-platform-net                        │
│           All services communicate via container DNS resolution           │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

**Request Flow:**
- User requests → Frontend (React, port 3000)
- API calls → WSO2 APIM (port 9443/8280/8243) [API Gateway]
- Data operations → Backend (FastAPI, port 8000)
- Data persistence → Oracle XE or PostgreSQL
- Batch jobs → Apache Airflow (port 8080)

### Services Overview

| Service | Stack | Version | Port(s) | Status |
|---------|-------|---------|---------|--------|
| Frontend | React + Vite | 18.2.0 + 5.4.21 | 3000 | ✅ Running |
| Backend | FastAPI + Python | 0.104.1 + 3.12 | 8000 | ✅ Running |
| Airflow | Apache Airflow | 3.0.0 | 8080 | ✅ Running |
| API Gateway | WSO2 APIM | 4.1.0 | 9443, 8280, 8243 | ✅ Running |
| Oracle DB | Oracle XE | 21.3.0 | 1521 | ✅ Running |
| PostgreSQL (CMS) | PostgreSQL | 15.3 | 5432 | ✅ Running |

---

## 📊 Database Architecture

The platform uses a **dedicated, isolated database architecture** for optimal security, scalability, and operational flexibility:

### Database Instances

#### 1. **Oracle Database (XE 21.3.0)** - Port 1521
- **Purpose**: Transactional data, system records
- **Container**: oracle-xe
- **Volume**: oracle_data (persistent storage)
- **Credentials**: 
  - Username: `sys`, Password: `oracle`
  - Service Name: `xepdb1`
- **Use Cases**:
  - CMS operational data
  - Historical transaction records
  - ETL source system
  - Reporting and analytics

#### 2. **PostgreSQL (CMS) - Port 5432**
- **Purpose**: Content Management System data, platform metadata
- **Container**: cms-postgresql
- **Database**: `cms`
- **Volume**: cms-data (persistent storage)
- **Credentials**: 
  - Username: `postgres`, Password: `postgres`
- **Use Cases**:
  - Application configuration
  - User management
  - Content repository
  - Reference data

### Database Connection Details

| Instance | Container | Host | Port (ext:int) | Database | User | Purpose |
|----------|-----------|------|----------------|----------|------|---------|
| **Oracle XE** | oracle-xe | N/A | 1521:1521 | xepdb1 | sys | Transactional |
| **PostgreSQL CMS** | cms-postgresql | cms-postgresql | 5432:5432 | cms | postgres | Platform data |

### Connection Strings

```bash
# Oracle
sqlplus sys/oracle@localhost:1521/xepdb1

# PostgreSQL CMS
psql -h localhost -p 5432 -U postgres -d cms

```

### Backup & Recovery

Each database maintains independent backup strategies:
- **Oracle**: Daily backups with 7-day retention
- **PostgreSQL CMS**: Transaction logs, point-in-time recovery

For complete backup procedures, see [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md#backup--disaster-recovery)

---

## 📱 Frontend - React with Bootstrap

### Status
✅ **Frontend is fully operational and accessible at http://localhost:3000**

### Overview

The frontend is a modern React application built with:
- **React 18.2.0** - UI framework
- **Vite 5.4.21** - Build tool for fast development
- **Bootstrap 5.3.0** - CSS framework for professional styling
- **Axios 1.15.0** - HTTP client for API communication

### Architecture

```
frontend/
├── src/
│   ├── components/
│   │   ├── MainLayout.jsx       # Main app layout with sidebar menu
│   │   ├── TestDatabase.jsx     # Database management page
│   │   ├── DataTable.jsx        # Reusable data table component
│   │   └── RecordForm.jsx       # CRUD form component
│   ├── hooks/
│   │   ├── useOracle.js         # Custom hook for Oracle operations
│   │   └── usePostgres.js       # Custom hook for PostgreSQL operations
│   ├── api/
│   │   └── client.js            # Axios HTTP client configuration
│   ├── App.jsx                  # Root component
│   ├── index.css                # Global styles
│   └── main.jsx                 # Entry point
├── index.html                   # HTML template
├── package.json                 # Dependencies
├── vite.config.js               # Vite configuration
└── tailwind.config.js           # Tailwind CSS configuration
```

### Local Development Setup

#### 1. Install Dependencies

```bash
cd frontend
npm install --legacy-peer-deps
```

#### 2. Start Development Server

```bash
npm run dev
```

Access at http://localhost:3000

#### 3. Build for Production

```bash
npm run build
```

---

## 🔧 FastAPI Backend

### Overview

The backend provides a RESTful API for CRUD operations on both Oracle and PostgreSQL databases.

### Architecture

```
backend/
├── app/
│   ├── __init__.py              # FastAPI app factory
│   ├── config.py                # Configuration
│   ├── database/
│   │   ├── oracle.py            # Oracle database operations
│   │   └── postgres.py          # PostgreSQL database operations
│   ├── routers/
│   │   ├── oracle.py            # Oracle API endpoints
│   │   └── postgres.py          # PostgreSQL API endpoints
│   └── schemas/
│       └── test.py              # Pydantic models
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── .env                         # Environment variables
```

### API Endpoints

#### Health Check
```
GET /health
Response: {"status": "healthy", "api": "CMS Platform API"}
```

#### Oracle Endpoints
```
GET    /oracle/test             # Get all records
GET    /oracle/test/{id}        # Get single record
POST   /oracle/test             # Create record
PUT    /oracle/test/{id}        # Update record
DELETE /oracle/test/{id}        # Delete record
```

#### PostgreSQL Endpoints
```
GET    /postgres/test           # Get all records
GET    /postgres/test/{id}      # Get single record
POST   /postgres/test           # Create record
PUT    /postgres/test/{id}      # Update record
DELETE /postgres/test/{id}      # Delete record
```

---

## 🛠️ Apache Airflow

### Overview

Data pipeline orchestration and scheduling platform for ETL workflows.

### Key Features
- **DAG-based workflow** definition
- **Scheduling** and monitoring
- **Backfill** capabilities
- **Retry** logic and error handling
- **Web UI** for management

### Access
- **URL**: http://localhost:8080
- **Default Credentials**: airflow / airflow

### DAGs Directory
```
airflow/dags/
├── hello_bash.py        # Basic Bash task DAG
├── hello_test.py        # Simple test DAG
└── test_oracle.py       # Oracle database testing
```

---

## 🌐 WSO2 APIM

### Overview

API Gateway and Management platform for API lifecycle management.

### Services
- **Admin Console**: https://localhost:9443/admin
- **Publisher**: https://localhost:9443/publisher
- **Developer Portal**: https://localhost:9443/devportal
- **Gateway (HTTP)**: http://localhost:8280
- **Gateway (HTTPS)**: https://localhost:8243

### Default Credentials
- **Username**: admin
- **Password**: admin

---

## 🗄️ Databases

### Oracle XE 21.3.0

```bash
# Connection Details
Host: localhost
Port: 1521
SID: xepdb1
Username: sys (SYSDBA)
Password: oracle

# Connection String
sqlplus sys/oracle@localhost:1521/xepdb1 as sysdba
```

### PostgreSQL 15.3

```bash
# Connection Details
Host: localhost
Port: 5432
Database: cms
Username: postgres
Password: postgres

# Connection String
psql -h localhost -U postgres -d cms
```

---

## 🐳 Docker Compose Configuration

### Service Dependencies

```
cms-postgresql ─┐
cms-oracle-xe  ├─► cms-backend ──┬─► cms-frontend
               ├─► cms-airflow   │
               └─► cms-apim      ────┘
```

### Network

All services communicate through a dedicated Docker bridge network:
```yaml
networks:
  cms-platform-net:
    driver: bridge
```

### Volumes

```yaml
volumes:
  oracle-data:        # Oracle database persistence
  postgres-data:      # PostgreSQL database persistence
  airflow-data:       # Airflow metadata
  wso2am-data:        # APIM repository data
  wso2am-logs:        # APIM logs
```

---

## 📋 Directory Structure

```
CMS-Platform/
├── backend/                 # FastAPI application
│   ├── app/
│   ├── run.py
│   └── requirements.txt
├── frontend/                # React application
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── airflow/                 # Apache Airflow
│   ├── dags/
│   ├── plugins/
│   ├── Dockerfile
│   └── docker-compose.yml
├── wso2-stack/              # WSO2 APIM
│   └── apim/
│       ├── Dockerfile
│       ├── deployment.toml
│       └── docker-compose.yml
├── oracle-db/               # Oracle utilities
├── postgresql-dwh/          # PostgreSQL utilities
├── superset/                # Data visualization (optional)
├── docker-compose.yml       # Main compose file
└── README.md                # This file
```

---

## 🚀 Common Commands

### View Service Status
```bash
# All services
docker compose ps

# Specific service
docker compose ps cms-backend

# With more details
docker compose ps --format "table {{.Service}}\t{{.Status}}"
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f cms-backend

# Last 50 lines
docker compose logs --tail 50 cms-backend
```

### Execute Commands in Container
```bash
# Shell access
docker compose exec cms-backend bash

# Run single command
docker compose exec cms-backend python -c "import sys; print(sys.version)"

# Database access
docker compose exec cms-postgresql psql -U postgres -d cms
```

### Restart Services
```bash
# Single service
docker compose restart cms-backend

# Multiple services
docker compose restart cms-backend cms-frontend

# All services
docker compose restart
```

### Rebuild Images
```bash
# Rebuild single service
docker compose build --no-cache cms-backend

# Rebuild all services
docker compose build --no-cache

# Build and start
docker compose up --build -d
```

---

## 🐛 Troubleshooting

### Services Not Starting

**Check logs**:
```bash
docker compose logs cms-service-name
```

**Common issues**:
- Port already in use: Change port mapping in docker-compose.yml
- Database not ready: Add health checks and increase wait time
- Out of memory: Increase Docker desktop memory allocation

### Database Connection Issues

**Verify containers are running**:
```bash
docker ps | grep -E "(oracle|postgres)"
```

**Test database connection**:
```bash
# Oracle
docker compose exec cms-oracle-xe sqlplus -version

# PostgreSQL
docker compose exec cms-postgresql psql -V
```

### API Integration Issues

**Test backend health**:
```bash
curl http://localhost:8000/health
```

**Check CORS configuration**:
- Frontend uses: http://localhost:3000
- Backend allows: allow_origins=["*"]

**Test specific endpoint**:
```bash
curl http://localhost:8000/oracle/test
```

---

## 🔐 Security Notes

### Default Credentials (Development Only)

⚠️ **These are for development/testing only. Change in production!**

- **Airflow**: airflow / airflow
- **WSO2 APIM**: admin / admin
- **Oracle**: sys / oracle
- **PostgreSQL**: postgres / postgres

### Recommended Production Changes

1. Change all default passwords
2. Enable HTTPS for all services
3. Configure firewall rules
4. Enable database backups
5. Set up monitoring and alerting
6. Use secrets management (Vault, etc.)

---

## 📚 Resources

- [React Documentation](https://react.dev)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Apache Airflow Documentation](https://airflow.apache.org)
- [WSO2 APIM Documentation](https://apim.docs.wso2.com)
- [Docker Documentation](https://docs.docker.com)

---

## 📝 License

All components are provided as-is for development and testing purposes.

---

## ✅ Verification Checklist

After starting the platform, verify all services:

- [ ] Frontend loads at http://localhost:3000
- [ ] Backend API responds at http://localhost:8000/health
- [ ] Airflow UI accessible at http://localhost:8080
- [ ] WSO2 APIM console at https://localhost:9443/admin
- [ ] Oracle database accessible on port 1521
- [ ] PostgreSQL accessible on port 5432
- [ ] All containers show "Up" status in `docker compose ps`

---

**Last Updated**: April 23, 2026
**Platform Version**: 1.0.0
**Status**: ✅ Production Ready
