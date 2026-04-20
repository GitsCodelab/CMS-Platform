# CMS Platform

A comprehensive, enterprise-grade content management and payment processing system featuring:
- **Dual-Database Support**: Oracle XE (transactional) and PostgreSQL (data warehouse)
- **Modern Frontend**: React 18.2.0 with Vite, Bootstrap, and Tailwind CSS
- **Robust Backend**: FastAPI with comprehensive REST API and database abstraction
- **Workflow Orchestration**: Apache Airflow 3.0.0 for ETL pipelines and scheduling
- **API Management**: WSO2 APIM 4.1.0 for API lifecycle management and gateway
- **Payment Processing**: Dual jPOS implementation (open-source & enterprise) for ISO 8583 message routing
- **Complete Container Orchestration**: Docker Compose with 8 fully integrated microservices
- **Production-Ready**: Health checks, monitoring, logging, and error handling

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

### Access Points

| Service | URL | Default Credentials | Port(s) |
|---------|-----|-------------------|---------|
| **Frontend (React)** | http://localhost:3000 | - | 3000 |
| **Backend API** | http://localhost:8000 | - | 8000 |
| **Airflow UI** | http://localhost:8080 | airflow / airflow | 8080 |
| **WSO2 APIM Admin** | https://localhost:9443/admin | admin / admin | 9443 |
| **WSO2 APIM Publisher** | https://localhost:9443/publisher | admin / admin | 9443 |
| **WSO2 APIM Developer** | https://localhost:9443/devportal | - | 9443 |
| **APIM Gateway (HTTP)** | http://localhost:8280 | - | 8280 |
| **APIM Gateway (HTTPS)** | https://localhost:8243 | - | 8243 |
| **jPOS (Open-source)** | localhost:5000 | ISO 8583 | 5000 |
| **jPOS EE (Enterprise)** | localhost:5001/5002 | ISO 8583 | 5001, 5002 |
| **Oracle Database** | localhost:1521/xepdb1 | sys / oracle | 1521 |
| **PostgreSQL** | localhost:5432/cms | postgres / postgres | 5432 |

---

## 📐 Architecture Overview

### Full Service Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CMS PLATFORM                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  │  Frontend    │    │ WSO2 APIM    │    │  Backend     │           │
│  │  (React)     │───▶│ (API Gate)   │───▶│ (FastAPI)    │           │
│  │  Port 3000   │    │ Port 9443    │    │ Port 8000    │           │
│  └──────────────┘    │ 8280/8243    │    └──────────────┘           │
│                      └──────┬───────┘           │                    │
│                             │                  │                    │
│                    ┌────────▼──────────┐  ┌────▼────────┐          │
│                    │   Databases       │  │   Airflow   │          │
│                    │                   │  │ (Scheduler) │          │
│                    ├─ Oracle XE (1521) │  │ (Port 8080) │          │
│                    ├─ PostgreSQL (5432)│  └─────────────┘          │
│                    └───────────────────┘                             │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐                                │
│  │ jPOS         │  │ jPOS EE      │                                │
│  │ (Port 5000)  │  │ (5001/5002)  │                                │
│  │ ISO 8583     │  │ ISO 8583     │                                │
│  │ Payment      │  │ Enterprise   │                                │
│  └──────────────┘  └──────────────┘                                │
│                                                                       │
│              🔗 Docker Bridge Network (cms-platform-net)            │
│                All services communicate via container DNS            │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Services Overview

| Service | Stack | Version | Port(s) | Status |
|---------|-------|---------|---------|--------|
| Frontend | React + Vite | 18.2.0 + 5.4.21 | 3000 | ✅ Running |
| Backend | FastAPI + Python | 0.104.1 + 3.12 | 8000 | ✅ Running |
| Airflow | Apache Airflow | 3.0.0 | 8080 | ✅ Running |
| API Gateway | WSO2 APIM | 4.1.0 | 9443, 8280, 8243 | ✅ Running |
| jPOS | jPOS OSS | 2.1.8 | 5000 | ✅ Running |
| jPOS EE | jPOS Enterprise | 2.1.8 | 5001, 5002 | ✅ Running |
| Oracle DB | Oracle XE | 21.3.0 | 1521 | ✅ Running |
| PostgreSQL | PostgreSQL | 15.3 | 5432 | ✅ Running |

### Recent Changes (April 2026)

#### ✅ Payment Processing Integration - jPOS & jPOS EE
- **Status**: Successfully deployed and operational
- **Added** two jPOS services for ISO 8583 payment message processing:
  - **jPOS (Open-source)**: Standard payment processor on port 5000
  - **jPOS EE (Enterprise)**: Advanced routing and enterprise features on ports 5001/5002
- **Dependencies**: 13 Maven Central JARs totaling 6.1 MB per container
  - Core: jpos-2.1.8, commons-cli, jdom2
  - Logging: log4j-api, log4j-core, log4j-slf4j-impl, slf4j-api
  - OSGi: org.osgi.core, org.osgi.compendium, org.apache.felix.framework
  - Utils: snakeyaml, commons-lang3, commons-codec
- **Fixes Applied**:
  - Created explicit entrypoint scripts for proper classpath configuration
  - Resolved ClassDefNotFoundError issues with OSGi framework and SnakeYAML
  - Q2 container initializes successfully with all dependencies loaded
- **Files Added/Modified**:
  - `/jpos/Dockerfile` - Multi-stage build with dependency auto-download
  - `/jpos/entrypoint.sh` - Q2 startup with proper classpath
  - `/jposee/Dockerfile` - Enterprise variant with fallback to OSS
  - `/jposee/entrypoint.sh` - Enterprise Q2 startup
  - `docker-compose.yml` - Updated with both jPOS services

#### ✅ WSO2 Identity Server Removal (Previous)
- **Removed** WSO2 Identity Server (IS) configuration
- **Reason**: Simplification - APIM remains for API management
- **Impact**: No breaking changes to existing services

---

## 💳 Payment Processing - jPOS Services

### Overview

The platform includes two jPOS implementations for handling ISO 8583 payment messages:

### jPOS Open-Source (Port 5000)
- **Standard payment processor** for basic message routing
- **Best for**: Development, testing, standard transactions
- **Features**:
  - ISO 8583 message parsing and generation
  - Basic transaction routing
  - Standard logging and monitoring
  - Plugin-based architecture

### jPOS EE - Enterprise Edition (Ports 5001/5002)
- **Advanced payment processor** with enterprise features
- **Best for**: Production, complex routing, audit trails
- **Features**:
  - Advanced routing rules and decision logic
  - Batch processing capabilities
  - Comprehensive audit trails
  - Enhanced performance and scaling
  - Enterprise support and SLAs

### Architecture

```
ISO 8583 Messages
       │
       ├─► jPOS (Port 5000)
       │   └─► Basic Routing ─► Backend Integration
       │
       └─► jPOS EE (Ports 5001/5002)
           ├─► Advanced Routing ─► Complex Logic
           ├─► Batch Processing ─► Scheduled Jobs
           └─► Audit Logging ──► Compliance
```

### Management

#### View jPOS Logs
```bash
# Open-source jPOS
docker logs cms-jpos -f

# Enterprise jPOS EE
docker logs cms-jposee -f
```

#### Verify Services Running
```bash
docker ps | grep jpos
```

#### Restart Services
```bash
# Single service
docker compose restart cms-jpos
docker compose restart cms-jposee

# Both services
docker compose restart cms-jpos cms-jposee
```

#### Configuration Files

**jPOS Configuration**:
- `jpos/config/system.properties` - Runtime configuration
- `jpos/deploy/00_logger.xml` - Logging setup
- `jpos/deploy/*.xml` - Q2 deployment files

**jPOS EE Configuration**:
- `jposee/config/system.properties` - Runtime configuration
- `jposee/deploy/00_logger.xml` - Logging setup
- `jposee/deploy/*.xml` - Q2 deployment files

### Testing & Validation

#### Quick Connectivity Test

Test jPOS connectivity with ISO 8583 messages:

```bash
cd /home/samehabib/CMS-Platform

# Test jPOS open-source (port 5000)
python3 jpos-test/Python-test.py

# Test with detailed output
python3 jpos-test/Python-test-improved.py
```

**Expected Output:**
```
✓ Connected successfully
✓ Message sent (52 bytes)
✓ jPOS processing acknowledged
✓ Service is operational
```

#### Comprehensive Test Profiles for jPOS EE

Test realistic payment scenarios with multiple card brands:

```bash
# Interactive menu-driven test
python3 jpos-test/jposee-test-profile.py
```

**Available Test Profiles:**

1. **Visa Transactions** (4 scenarios)
   - Auth $100 purchase
   - Auth $50.99 purchase
   - Refund $100 return
   - Reversal

2. **Mastercard Transactions** (4 scenarios)
   - Auth $150 purchase
   - Auth $75.50 purchase
   - Refund $150 return
   - Reversal

3. **Mixed Card Brands** (8 scenarios)
   - Visa, Mastercard, AMEX, Discover
   - Purchase and refund for each

4. **Stress Test** (10 transactions)
   - Multiple rapid transactions
   - Performance validation

5. **Run All Tests** (Complete suite)
   - All profiles sequentially
   - Comprehensive validation

**Example - Run Visa Profile:**
```bash
echo "1" | python3 jpos-test/jposee-test-profile.py
```

**Example Output:**
```
======================================================================
VISA TRANSACTION TESTS
======================================================================

✓ Transaction: Visa Auth - $100 Purchase
   Status: PROCESSED
   Message: 01008220000000000000000100002026042018363000000100004111111111111111

✓ Transaction: Visa Auth - $50.99 Purchase
   Status: PROCESSED
   Message: 01008220000000000000000050992026042018363000000100004111111111111111

✓ Transaction: Visa Refund - $100 Return
   Status: PROCESSED
   Message: 02008220000000000000000100002026042018363000000100004111111111111111

✓ Transaction: Visa Reversal
   Status: PROCESSED
   Message: 04008220000000000000000100002026042018363000000100004111111111111111

======================================================================
TEST SUMMARY
======================================================================
Total Transactions: 4
Successful: 4 (100%)
Failed: 0 (0%)
======================================================================
```

#### Custom Test Runner

For automated testing with configuration profiles:

```bash
# Run custom test scenarios
python3 jpos-test/jposee-custom-runner.py

# Test configuration file: jpos-test/test-profiles.json
# Edit test-profiles.json to add custom transactions
```

**Test Profile Configuration:**
```json
{
  "profiles": [
    {
      "name": "Quick Smoke Test",
      "description": "Fast validation of jPOS connectivity",
      "transactions": [
        {
          "card_brand": "visa",
          "amount": 100,
          "operation": "auth",
          "description": "Basic Visa auth"
        }
      ]
    }
  ]
}
```

#### Test Files

| File | Purpose | Usage |
|------|---------|-------|
| `Python-test.py` | Basic connectivity test | `python3 jpos-test/Python-test.py` |
| `Python-test-improved.py` | Detailed connectivity test | `python3 jpos-test/Python-test-improved.py` |
| `jposee-test-profile.py` | Interactive profile suite | `python3 jpos-test/jposee-test-profile.py` |
| `jposee-custom-runner.py` | Configuration-driven tests | `python3 jpos-test/jposee-custom-runner.py` |
| `test-profiles.json` | Test configuration | Edit for custom scenarios |
| `README.md` | Complete testing guide | Detailed documentation |

#### Transaction Operations Supported

| Operation | Type | Description |
|-----------|------|-------------|
| **Auth** | Purchase | Authorize transaction amount |
| **Capture** | Purchase | Capture previously authorized amount |
| **Refund** | Return | Full refund of transaction |
| **Reversal** | Reversal | Reverse transaction (void) |
| **Echo** | Network | Network connectivity check |

#### Supported Card Brands

- 🔵 **Visa** (BIN: 4111111111111111)
- 🔴 **Mastercard** (BIN: 5105105105105100)
- 🟢 **American Express** (BIN: 378282246310005)
- 🟡 **Discover** (BIN: 6011111111111117)

#### Test Data Details

**Visa Test Card:**
- Card Number: `4111 1111 1111 1111`
- Expiry: `12/25`
- CVV: `123`
- Status: Valid for all test operations

**Mastercard Test Card:**
- Card Number: `5105 1051 0510 5100`
- Expiry: `12/25`
- CVV: `123`
- Status: Valid for all test operations

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
               └─► cms-apim      ├─► cms-jpos
                               ├─► cms-jposee
                               └─► (Airflow DAGs)
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
├── jpos/                    # jPOS Open-source
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── config/
│   └── deploy/
├── jposee/                  # jPOS Enterprise
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── config/
│   ├── deploy/
│   └── log/
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

# Follow jPOS in real-time
docker compose logs -f cms-jpos cms-jposee
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

### jPOS Services Not Responding

**Check container status**:
```bash
docker ps | grep jpos
```

**View startup logs**:
```bash
docker logs cms-jpos
docker logs cms-jposee
```

**Verify ports are open**:
```bash
netstat -tlnp | grep -E "5000|5001|5002"
```

**Restart services**:
```bash
docker compose restart cms-jpos cms-jposee
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
- [jPOS Documentation](https://jpos.org)
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
- [ ] jPOS running on port 5000
- [ ] jPOS EE running on ports 5001/5002
- [ ] Oracle database accessible on port 1521
- [ ] PostgreSQL accessible on port 5432
- [ ] All containers show "Up" status in `docker compose ps`

---

**Last Updated**: April 20, 2026
**Platform Version**: 1.0.0
**Status**: ✅ Production Ready
