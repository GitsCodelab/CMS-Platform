# CMS Platform - API and Data Reconciliation Solution

**Version**: 1.2  
**Status**: Production Ready  
**Last Updated**: April 29, 2026

---

## Overview

CMS Platform is a unified stack for API management, backend services, workflow orchestration, and data operations.

Core components:
- WSO2 API Manager 4.3.x for API lifecycle and gateway management
- FastAPI backend for business APIs and database integration
- React frontend for operational UI
- Apache Airflow for scheduled workflows and automation
- Oracle + PostgreSQL for transactional and analytical workloads

---

## Quick Start

### 1. Start all services

```bash
docker-compose up -d
```

### 2. Verify status

```bash
docker-compose ps
```

### 3. Access services

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- APIM Admin/Publisher: https://localhost:9443
- APIM HTTP Gateway: http://localhost:8280
- APIM HTTPS Gateway: https://localhost:8243
- Airflow: http://localhost:8080

---

## Service Matrix

| Service | URL/Port | Purpose |
|---|---|---|
| Frontend | http://localhost:3000 | User interface |
| Backend API | http://localhost:8000 | REST API |
| APIM Admin | https://localhost:9443 | API management |
| APIM Gateway (HTTP) | http://localhost:8280 | HTTP API traffic |
| APIM Gateway (HTTPS) | https://localhost:8243 | HTTPS API traffic |
| Airflow UI | http://localhost:8080 | Workflow orchestration |
| Oracle XE | localhost:1521 | Transactional data |
| PostgreSQL | localhost:5432 | APIM + DWH data |

---

## Credentials (Development)

### APIM
- Username: admin
- Password: admin

### Airflow
- Username: airflow
- Password: airflow

### Oracle
- Username: MAIN
- Password: main123
- Service name: xepdb1

### PostgreSQL
- Username: postgres
- Password: postgres

Change all defaults before production use.

---

## Common Commands

```bash
# Start platform
docker-compose up -d

# Stop platform
docker-compose down

# Check container state
docker-compose ps

# Tail logs
docker-compose logs -f cms-apim
docker-compose logs -f cms-backend
docker-compose logs -f cms-airflow

# Backend health check
curl http://localhost:8000/health
```

---

## Documentation

- Main index: [docs/INDEX.md](docs/INDEX.md)
- API registration guide: [docs/api/API_REGISTRATION_GUIDE.md](docs/api/API_REGISTRATION_GUIDE.md)
- Deployment guide: [docs/deployment/PRODUCTION_DEPLOYMENT.md](docs/deployment/PRODUCTION_DEPLOYMENT.md)
- Setup guide: [docs/setup/APIM_SETUP_GUIDE.md](docs/setup/APIM_SETUP_GUIDE.md)
- Database initialization: [docs/setup/DATABASE_INIT_README.md](docs/setup/DATABASE_INIT_README.md)
- Verification guide: [docs/guides/IMPLEMENTATION_VERIFICATION.md](docs/guides/IMPLEMENTATION_VERIFICATION.md)

---

## Project Structure

```text
CMS-Platform/
├── README.md
├── docker-compose.yml
├── frontend/
├── backend/
├── airflow/
├── wso2-stack/
├── oracle-db/
├── postgresql-dwh/
├── docs/
└── scripts/
```

---

## Troubleshooting

- Check all containers: `docker-compose ps`
- Inspect service logs: `docker-compose logs -f <service>`
- APIM setup issues: [docs/setup/APIM_SETUP_GUIDE.md](docs/setup/APIM_SETUP_GUIDE.md)
- General troubleshooting: [docs/troubleshooting/README.md](docs/troubleshooting/README.md)

---

## License

See [LICENSE](LICENSE).
