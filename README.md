# CMS-Platform

A comprehensive data orchestration platform built with Apache Airflow, Oracle, PostgreSQL, and WSO2 stack.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Linux/WSL2 environment

### Startup

```bash
# Start all services
docker compose up -d

# Verify all containers are running
docker ps

# Access Airflow UI
http://localhost:8080
```

**Airflow Credentials:**
- **Username:** airflow
- **Password:** airflow

## Architecture

### Services

| Service | Port | Description |
|---------|------|-------------|
| **FastAPI Backend** | 8000 | REST API for dual-database CRUD operations |
| **Airflow (Standalone)** | 8080 | Data orchestration & scheduling |
| **Oracle Database** | 1521 | Primary data source |
| **PostgreSQL DWH** | 5432 | Data warehouse |
| **Superset** | 8088 | Analytics & visualization |
| **WSO2 APIM** | 9443 | API management |

## FastAPI Backend

### Overview

The backend provides a RESTful API for CRUD operations on both Oracle and PostgreSQL databases using FastAPI with a professional modular architecture.

### Architecture

The backend is organized using separation of concerns:

```
backend/
├── app/
│   ├── __init__.py           # FastAPI application factory
│   ├── config.py             # Configuration management
│   ├── schemas/              # Pydantic request/response models
│   │   └── __init__.py
│   ├── database/             # Database connectors
│   │   ├── __init__.py
│   │   ├── oracle.py         # Oracle database operations
│   │   └── postgres.py       # PostgreSQL database operations
│   └── routers/              # API endpoints
│       ├── __init__.py
│       ├── oracle.py         # Oracle endpoints
│       └── postgres.py       # PostgreSQL endpoints
├── run.py                    # Application entry point
├── requirements.txt          # Dependencies
└── .env                      # Configuration variables
```

### Setup

```bash
# Backend starts automatically with Docker Compose
docker compose up -d

# Or manually start just the backend
docker compose up -d cms-backend

# Check health
curl http://localhost:8000/health
```

### API Endpoints

#### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "api": "CMS Platform API",
  "version": "1.0.0"
}
```

#### Oracle Test Table

```bash
# Get all records
GET /oracle/test

# Get record by ID
GET /oracle/test/{id}

# Create record
POST /oracle/test
Body: {"id": 10, "name": "Test", "description": "Desc", "status": "pending"}

# Update record
PUT /oracle/test/{id}
Body: {"name": "Updated", "status": "active"}

# Delete record
DELETE /oracle/test/{id}
```

#### PostgreSQL Test Table

```bash
# Get all records
GET /postgres/test

# Get record by ID
GET /postgres/test/{id}

# Create record
POST /postgres/test
Body: {"name": "Test", "description": "Desc", "status": "pending"}

# Update record
PUT /postgres/test/{id}
Body: {"name": "Updated", "status": "active"}

# Delete record
DELETE /postgres/test/{id}
```

### Configuration

Environment variables in `backend/.env`:

```
ORACLE_HOST=cms-oracle-xe
ORACLE_PORT=1521
ORACLE_USER=system
ORACLE_PASSWORD=oracle
ORACLE_SERVICE=xepdb1

POSTGRES_HOST=cms-postgresql
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=cms

API_TITLE=CMS Platform API
API_VERSION=1.0.0
```

### Interactive API Documentation

FastAPI provides auto-generated documentation:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Initialization

To populate test data:

```bash
python backend/setup_test_tables.py
```

This creates test tables with sample data in both databases.



### Database Connection

Airflow uses PostgreSQL for metadata storage:
```
Host: cms-postgresql
Port: 5432
User: postgres
Password: postgres
Database: cms
```

Connection URI: `postgresql+psycopg2://postgres:postgres@cms-postgresql:5432/cms`

### Authentication

SimpleAuthManager is configured with credentials stored in:
- **File:** `airflow/simple_auth_manager_passwords.json`
- **Default User:** airflow / airflow

## Database Connections

### Oracle Connection (`oracle_main`)

Airflow connects to Oracle XE database:
```
Type:         Oracle
Host:         cms-oracle-xe
Port:         1521
Login:        system
Password:     oracle
Service Name: xepdb1
```

**Connection URI:** `oracle://system:oracle@cms-oracle-xe:1521/?service_name=xepdb1`

### PostgreSQL Connection (`postgres_main`)

Airflow connects to PostgreSQL:
```
Type:     PostgreSQL
Host:     cms-postgresql
Port:     5432
Username: postgres
Password: postgres
Database: cms
```

**Connection URI:** `postgresql://postgres:postgres@cms-postgresql:5432/cms`

### Setup Connections

Use the automated setup script to create or recreate connections:

```bash
# Create connections (if they don't exist)
bash airflow/scripts/create_connections.sh

# Force recreate connections
bash airflow/scripts/create_connections.sh --force
```

The script will:
- ✓ Create `oracle_main` connection
- ✓ Create `postgres_main` connection
- ✓ Verify both connections are accessible
- ✓ Test connectivity to both databases

## Important Fixes Applied

### 1. Database Connection Issue
**Problem:** Airflow was configured to connect to `airflow-postgres:5432`, but the actual database container is named `cms-postgresql`.

**Fix:** Updated `docker-compose.yml` to use the correct hostname:
```yaml
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://postgres:postgres@cms-postgresql:5432/cms
```

### 2. Healthcheck Configuration
**Problem:** Healthcheck was using `pg_isready` on the Airflow container (which checks PostgreSQL).

**Fix:** Changed to HTTP-based healthcheck:
```yaml
healthcheck:
  test: ["CMD", "curl", "--fail", "http://localhost:8080/ui/"]
  interval: 15s
  timeout: 10s
  retries: 5
  start_period: 60s
```

### 3. File Permissions
**Problem:** DAG processor couldn't create log directories due to permission issues.

**Fix:**
```bash
# Fix logs directory permissions
sudo chown -R 50000:0 airflow/logs/
sudo chmod -R 755 airflow/logs/

# Fix passwords file permissions
sudo chown 50000:0 airflow/simple_auth_manager_passwords.json
sudo chmod 644 airflow/simple_auth_manager_passwords.json
```

**Note:** Airflow runs as user UID 50000 inside the container.

## Troubleshooting

### Airflow won't start

1. **Check container logs:**
   ```bash
   docker logs cms-airflow
   ```

2. **Verify database connectivity:**
   ```bash
   docker exec cms-airflow airflow db check
   ```

3. **Reset permissions if needed:**
   ```bash
   sudo chown -R 50000:0 airflow/
   sudo chmod -R 755 airflow/
   ```

### Permission Denied Errors

If you see `PermissionError: [Errno 13]`, run:
```bash
sudo chown -R 50000:0 airflow/
sudo chmod -R u+rwx airflow/
```

## Project Structure

```
.
├── backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── __init__.py      # FastAPI factory
│   │   ├── config.py        # Settings management
│   │   ├── schemas/         # Pydantic models
│   │   ├── database/        # DB connectors
│   │   └── routers/         # API endpoints
│   ├── run.py               # Entry point
│   ├── requirements.txt     # Dependencies
│   ├── .env                 # Configuration
│   └── setup_test_tables.py # Test data initialization
├── airflow/
│   ├── dags/              # DAG definitions
│   ├── logs/              # DAG execution logs
│   ├── plugins/           # Custom Airflow plugins
│   ├── scripts/           # Initialization scripts
│   └── docker-compose.yml # Airflow-specific services
├── oracle-db/            # Oracle database files
├── postgresql-dwh/       # PostgreSQL DWH files
├── superset/             # Superset configuration
├── wso2-stack/           # WSO2 API Management
└── docker-compose.yml    # Main orchestration
```

## Development

### DAGs

Place your DAG Python files in `airflow/dags/`. They will be automatically discovered.

Example:
```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG('my_dag', start_date=datetime(2024, 1, 1)) as dag:
    task = BashOperator(task_id='hello', bash_command='echo "Hello"')
```

### Connections

Create connections in Airflow UI or via CLI:
```bash
docker exec cms-airflow airflow connections add \
  --conn-id my_connection \
  --conn-type postgres \
  --conn-host localhost \
  --conn-port 5432
```

### Testing Database Connections

A test DAG is included to verify both Oracle and PostgreSQL connections:

```bash
# Test connections via DAG
docker compose exec cms-airflow airflow dags test test_connections

# Or from the Airflow UI: http://localhost:8080
# Navigate to DAGs → test_connections → Trigger DAG
```

The test DAG will run two tasks:
- `test_oracle` - Queries Oracle database (`SELECT name FROM v$database`)
- `test_postgres` - Queries PostgreSQL database (`SELECT NOW()`)

Both tasks must complete successfully for connections to be working correctly.

## Maintenance

### Backup

Logs and metadata are stored in volumes managed by Docker.

### Cleanup

To reset everything:
```bash
docker compose down -v
```

## License

See LICENSE file for details.