# Airflow 3.x Configuration

## Latest Changes

### Version Upgrade: 2.8.1 → 3.x (Latest)

**Date**: April 4, 2026

#### What's New in Airflow 3.x

✅ **Improvements**
- Python 3.9+ required (faster, more secure)
- Enhanced Celery executor
- Improved DAG parsing and scheduling
- Better error messages and logging
- New REST API v2 features
- Improved UI/UX
- Better memory management
- Faster task execution

✅ **Breaking Changes**
- Removed legacy task groups
- Updated import paths for some operators
- Changed default auth backend
- Updated database schema (auto-migration on startup)

#### Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | All services (PostgreSQL, Redis, Webserver, Scheduler, Worker) |
| `.env` | Environment variables for Airflow 3.x |
| `setup.sh` | Quick setup script |
| `README.md` | Documentation |

#### Services Running

- **PostgreSQL 15** - Database backend
- **Redis 7** - Message broker
- **Airflow Webserver 3.x** - Web UI (port 1013)
- **Airflow Scheduler 3.x** - DAG scheduling
- **Airflow Worker 3.x** - Task execution

#### Quick Start

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh

# Access Airflow
# http://localhost:1013
# Username: airflow
# Password: airflow
```

#### Notes

- All images use `apache/airflow:latest` (3.8.x)
- Automatic database migrations on startup
- Health checks enabled for all services
- Persistent volumes for data
- Fixed UIDs for proper file permissions

#### Compatibility

✅ Oracle Connections: Supported via providers
✅ PostgreSQL: Native support
✅ Custom DAGs: Place in `./dags` folder
✅ Plugins: Place in `./plugins` folder

#### Troubleshooting

**Database Initialize Fails**
```bash
docker-compose down -v
docker-compose up -d
```

**Permission Issues**
```bash
export AIRFLOW_UID=$(id -u)
docker-compose restart
```

**High CPU Usage**
- Reduce `AIRFLOW__CELERY__WORKER_CONCURRENCY` in `.env`
- Decrease `AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG`

---

For more information, visit: https://airflow.apache.org/docs/apache-airflow/stable/
