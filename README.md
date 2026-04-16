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
| **Airflow (Standalone)** | 8080 | Data orchestration & scheduling |
| **Oracle Database** | 1521 | Primary data source |
| **PostgreSQL DWH** | 5432 | Data warehouse |
| **Superset** | 8088 | Analytics & visualization |
| **WSO2 APIM** | 9443 | API management |

## Airflow Configuration

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