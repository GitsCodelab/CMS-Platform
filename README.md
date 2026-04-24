# CMS Platform - Complete API & Data Reconciliation Solution

**Version**: 1.0  
**Status**: ✅ Production Ready  
**Last Updated**: April 24, 2026  

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Platform Overview](#platform-overview)
3. [Architecture](#architecture)
4. [Services & Access Points](#services--access-points)
5. [Getting Started by Role](#getting-started-by-role)
6. [Complete Documentation](#complete-documentation)
7. [Quick Reference](#quick-reference)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### 1. Start All Services
```bash
docker-compose up -d
```

### 2. Verify Services
```bash
docker-compose ps
```

### 3. Access Platform
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **APIM Gateway**: https://localhost:9443
- **Airflow**: http://localhost:8080

### 4. Next Steps
See [Getting Started by Role](#getting-started-by-role) for your specific workflow.

---

## 📚 Platform Overview

**CMS Platform** is a comprehensive API and data reconciliation solution featuring:

- **WSO2 API Manager 4.3.0**: Enterprise API gateway with lifecycle management
- **FastAPI Backend**: High-performance REST API with Oracle/PostgreSQL integration
- **React Frontend**: Modern, responsive UI with Tailwind CSS
- **Apache Airflow**: Workflow orchestration and data pipeline automation
- **Multi-Database Support**: Oracle, PostgreSQL (DWH), and dedicated APIM database

### Key Capabilities

✅ **API Lifecycle Management**
- API registration, versioning, and deployment
- Multiple deployment targets (Production, Sandbox)
- Policy enforcement (rate limiting, throttling, authentication)
- Built-in monitoring and analytics

✅ **High-Performance Backend**
- FastAPI with async support
- Oracle and PostgreSQL integration
- RESTful API design with OpenAPI documentation
- Comprehensive error handling

✅ **Workflow Orchestration**
- Apache Airflow for scheduled jobs
- Data pipeline automation
- Multi-database operations
- Audit logging

✅ **Enterprise-Grade Features**
- Role-based access control
- SSL/TLS encryption
- Comprehensive logging
- Health checks and monitoring

---

## 🏗️ Architecture

### Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│                   http://localhost:3000                      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
┌────────────────────────▼────────────────────────────────────┐
│          WSO2 API Manager (APIM) 4.3.0 Gateway              │
│          https://localhost:9443 (Admin/Publisher)           │
│          http://localhost:8280 (HTTP Gateway)               │
│          https://localhost:8243 (HTTPS Gateway)             │
└────────────────────────┬────────────────────────────────────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
┌──────────▼───┐  ┌──────▼───┐  ┌────▼──────────┐
│  Backend API │  │ Airflow  │  │  Oracle DB    │
│ FastAPI      │  │          │  │  (Primary)    │
│ :8000        │  │ :8080    │  │  :1521        │
└──────┬───────┘  └──────┬───┘  └─────┬─────────┘
       │                 │            │
       └─────────────────┼────────────┘
                         │
           ┌─────────────┼──────────────┐
           │             │              │
    ┌──────▼──────┐  ┌───▼──────┐  ┌────▼────┐
    │PostgreSQL   │  │APIM DB   │  │ Redis   │
    │(DWH)        │  │(wso2am)  │  │(Cache)  │
    │:5432        │  │:5432     │  │:6379    │
    └─────────────┘  └──────────┘  └─────────┘
```

### Data Flow

```
User Interface (Frontend)
    ↓ HTTP/HTTPS
API Manager Gateway (APIM 4.3.0)
    ↓ Policy Enforcement, Rate Limiting, Auth
Backend API (FastAPI)
    ↓ REST Endpoints
┌─────────────────┬──────────────────┬──────────────┐
│                 │                  │              │
↓                 ↓                  ↓              ↓
Oracle DB      PostgreSQL DWH    Airflow Jobs    Cache Layer
(Transactional) (Analytics)      (Orchestration)  (Performance)
```

---

## 🔌 Services & Access Points

### Core Services

| Service | URL | Port | Purpose | Status |
|---------|-----|------|---------|--------|
| **Frontend** | http://localhost:3000 | 3000 | React UI | ✅ Active |
| **Backend API** | http://localhost:8000 | 8000 | FastAPI REST | ✅ Active |
| **APIM Admin** | https://localhost:9443 | 9443 | API Manager UI | ✅ Active |
| **APIM Gateway** | http://localhost:8280 | 8280 | HTTP Gateway | ✅ Active |
| **APIM Gateway** | https://localhost:8243 | 8243 | HTTPS Gateway | ✅ Active |
| **Airflow** | http://localhost:8080 | 8080 | Workflow UI | ✅ Active |

### Databases

| Database | Host | Port | Type | Purpose |
|----------|------|------|------|---------|
| **Oracle XE** | localhost | 1521 | Oracle XE | Primary transactional DB |
| **PostgreSQL** | localhost | 5432 | PostgreSQL 15 | APIM + DWH database |

### Credentials

#### APIM (WSO2 API Manager)
- **URL**: https://localhost:9443/admin
- **Username**: admin
- **Password**: admin
- **Note**: Change in production

#### Backend API
- **Base URL**: http://localhost:8000
- **OpenAPI Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

#### Airflow
- **URL**: http://localhost:8080
- **Username**: airflow
- **Password**: airflow

#### Databases
- **Oracle**: 
  - Username: MAIN
  - Password: main123
  - Service: xepdb1
- **PostgreSQL**: 
  - Username: postgres
  - Password: postgres

---

## 👥 Getting Started by Role

### 👤 **New Users** - Start Here!
**Goal**: Understand the platform and get familiar with basic operations

**Recommended Path**:
1. Start services: `docker-compose up -d`
2. Access Frontend: http://localhost:3000
3. Verify everything is working: [docs/guides/IMPLEMENTATION_VERIFICATION.md](docs/guides/IMPLEMENTATION_VERIFICATION.md)
4. Explore APIs in APIM: https://localhost:9443/publisher
5. Read: [docs/setup/SETUP_NEW_SERVER.md](docs/setup/SETUP_NEW_SERVER.md)

---

### 👨‍💻 **Developers** - Build & Extend
**Goal**: Create and register new APIs, integrate with the platform

**Recommended Path**:
1. Backend API Development: [docs/api/API_REGISTRATION_GUIDE.md](docs/api/API_REGISTRATION_GUIDE.md)
2. Register Your API: Use `register_api.sh` script
   ```bash
   bash wso2-stack/apim/register_api.sh \
     --name "Your API" \
     --context "/your-api" \
     --backend "http://your-backend:port/path"
   ```
3. API Lifecycle Management: [docs/api/API_REGISTRATION_GUIDE.md](docs/api/API_REGISTRATION_GUIDE.md#api-lifecycle-management)
4. Testing & Deployment: [docs/guides/IMPLEMENTATION_VERIFICATION.md](docs/guides/IMPLEMENTATION_VERIFICATION.md)

---

### ⚙️ **DevOps / SRE** - Deploy & Monitor
**Goal**: Manage infrastructure, deployments, and system reliability

**Recommended Path**:
1. Infrastructure Setup: [docs/deployment/PRODUCTION_DEPLOYMENT.md](docs/deployment/PRODUCTION_DEPLOYMENT.md)
2. APIM Configuration: [wso2-stack/apim/DEFAULT_GATEWAY_README.md](wso2-stack/apim/DEFAULT_GATEWAY_README.md)
3. Database Management: [docs/setup/DATABASE_INIT_README.md](docs/setup/DATABASE_INIT_README.md)
4. Monitoring & Health Checks: [docs/guides/IMPLEMENTATION_VERIFICATION.md](docs/guides/IMPLEMENTATION_VERIFICATION.md#health-checks)
5. Troubleshooting: [docs/troubleshooting/](docs/troubleshooting/)

---

### 🔧 **System Administrators** - Manage & Maintain
**Goal**: Oversee system operations, security, and compliance

**Recommended Path**:
1. Complete Setup Guide: [docs/setup/APIM_SETUP_GUIDE.md](docs/setup/APIM_SETUP_GUIDE.md)
2. Production Deployment: [docs/deployment/PRODUCTION_DEPLOYMENT.md](docs/deployment/PRODUCTION_DEPLOYMENT.md)
3. Security Configuration: [wso2-stack/apim/DEFAULT_GATEWAY_README.md](wso2-stack/apim/DEFAULT_GATEWAY_README.md#security-configuration)
4. Monitoring: Check [docs/guides/](docs/guides/) for verification procedures
5. Troubleshooting: [docs/troubleshooting/](docs/troubleshooting/)

---

## 📖 Complete Documentation

### Documentation Structure

The `docs/` directory provides organized, role-based documentation:

```
docs/
├── INDEX.md                          ← Start here for documentation
├── setup/                            ← Initial setup & configuration
│   ├── SETUP_NEW_SERVER.md
│   ├── APIM_SETUP_GUIDE.md
│   ├── PHASE_1_IMPLEMENTATION_GUIDE.md
│   ├── DATABASE_INIT_README.md
│   └── README.md
├── api/                              ← API development & registration
│   ├── API_REGISTRATION_GUIDE.md
│   └── README.md
├── deployment/                       ← Production deployment
│   ├── PRODUCTION_DEPLOYMENT.md
│   └── README.md
├── guides/                           ← Additional guides & verification
│   ├── IMPLEMENTATION_VERIFICATION.md
│   └── README.md
├── troubleshooting/                  ← Issue resolution
│   └── README.md
└── archived/                         ← Legacy documentation
    └── README.md
```

### Quick Document Links

| Document | Purpose | Audience |
|----------|---------|----------|
| [docs/INDEX.md](docs/INDEX.md) | **Main documentation index** | Everyone |
| [docs/setup/APIM_SETUP_GUIDE.md](docs/setup/APIM_SETUP_GUIDE.md) | Complete APIM initialization | DevOps, Admins |
| [docs/api/API_REGISTRATION_GUIDE.md](docs/api/API_REGISTRATION_GUIDE.md) | API registration & lifecycle | Developers |
| [docs/deployment/PRODUCTION_DEPLOYMENT.md](docs/deployment/PRODUCTION_DEPLOYMENT.md) | Production deployment procedures | DevOps, Admins |
| [docs/guides/IMPLEMENTATION_VERIFICATION.md](docs/guides/IMPLEMENTATION_VERIFICATION.md) | Verification & health checks | Everyone |
| [wso2-stack/apim/DEFAULT_GATEWAY_README.md](wso2-stack/apim/DEFAULT_GATEWAY_README.md) | Default gateway configuration | DevOps, Developers |
| [docs/setup/DATABASE_INIT_README.md](docs/setup/DATABASE_INIT_README.md) | Database initialization | DBAs, DevOps |

---

## 🔍 Quick Reference

### Essential Scripts

```bash
# 1. Start platform
docker-compose up -d

# 2. Check status
docker-compose ps

# 3. View logs
docker-compose logs -f cms-apim      # APIM logs
docker-compose logs -f cms-backend   # Backend logs
docker-compose logs -f cms-frontend  # Frontend logs

# 4. Register an API
bash wso2-stack/apim/register_api.sh \
  --name "API Name" \
  --context "/api-context" \
  --backend "http://backend:port/path"

# 5. Access APIM
# Admin: https://localhost:9443/admin
# Publisher: https://localhost:9443/publisher
# Developer Portal: https://localhost:9443/devportal

# 6. Test backend API
curl http://localhost:8000/health
curl http://localhost:8000/oracle/test
curl http://localhost:8000/postgres/test
```

### API Endpoint Examples

```bash
# Oracle Test API (via APIM gateway)
curl http://localhost:8280/cms/oracle/v1.0.0

# PostgreSQL Test API (via APIM gateway)
curl http://localhost:8280/cms/postgres/v1.0.0

# Backend direct access
curl http://localhost:8000/oracle/test
curl http://localhost:8000/postgres/test

# With authentication
curl -H "Authorization: Bearer <token>" \
  https://localhost:8243/cms/oracle/v1.0.0
```

### Common Tasks

| Task | How To | Documentation |
|------|--------|---------------|
| Register new API | Use `register_api.sh` | [API_REGISTRATION_GUIDE.md](docs/api/API_REGISTRATION_GUIDE.md) |
| Deploy to production | Follow deployment guide | [PRODUCTION_DEPLOYMENT.md](docs/deployment/PRODUCTION_DEPLOYMENT.md) |
| Check system health | Run verification | [IMPLEMENTATION_VERIFICATION.md](docs/guides/IMPLEMENTATION_VERIFICATION.md) |
| Initialize databases | Run init scripts | [DATABASE_INIT_README.md](docs/setup/DATABASE_INIT_README.md) |
| Configure gateway | Use DEFAULT_GATEWAY_README.md | [DEFAULT_GATEWAY_README.md](wso2-stack/apim/DEFAULT_GATEWAY_README.md) |

---

## 🆘 Troubleshooting

### Common Issues

**Q: Services won't start**
- Check Docker is running: `docker ps`
- Check port availability: `lsof -i :3000` etc.
- See: [docs/troubleshooting/README.md](docs/troubleshooting/README.md)

**Q: Can't connect to APIM**
- Verify APIM is running: `docker logs cms-apim`
- Check https://localhost:9443/admin (accept self-signed cert)
- See: [docs/setup/APIM_SETUP_GUIDE.md](docs/setup/APIM_SETUP_GUIDE.md)

**Q: API registration fails**
- Check APIM connectivity: `curl -k https://localhost:9443/`
- Verify backend is reachable from APIM container
- See: [docs/api/API_REGISTRATION_GUIDE.md](docs/api/API_REGISTRATION_GUIDE.md)

**Q: Database connection issues**
- Verify databases are running: `docker-compose ps`
- Check credentials in configuration
- See: [docs/setup/DATABASE_INIT_README.md](docs/setup/DATABASE_INIT_README.md)

### Getting Help

1. **Quick answers**: Check [docs/troubleshooting/](docs/troubleshooting/)
2. **Setup issues**: See [docs/setup/](docs/setup/)
3. **API problems**: See [docs/api/](docs/api/)
4. **Deployment**: See [docs/deployment/](docs/deployment/)
5. **Full index**: See [docs/INDEX.md](docs/INDEX.md)

---

## 📊 Project Structure

```
CMS-Platform/
├── README.md                          ← You are here
├── docker-compose.yml                 ← Main orchestration
├── docs/                              ← Complete documentation
├── frontend/                          ← React UI
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── backend/                           ← FastAPI REST
│   ├── app/
│   ├── requirements.txt
│   └── run.py
├── wso2-stack/                        ← API Manager & IS
│   ├── apim/                          ← APIM configuration
│   │   ├── DEFAULT_GATEWAY_README.md
│   │   ├── default-gateway-config.json
│   │   ├── register_api.sh
│   │   └── deployment.toml
│   └── wso2is/
├── oracle-db/                         ← Oracle database
├── postgresql-dwh/                    ← PostgreSQL database
├── airflow/                           ← Airflow orchestration
├── superset/                          ← Analytics (optional)
└── scripts/                           ← Utility scripts
```

---

## 🔐 Security Notes

- **Development Mode**: Uses default credentials - change before production
- **SSL/TLS**: APIM uses self-signed certificates - configure proper certs for production
- **Database Passwords**: Change default credentials in `.env` and `docker-compose.yml`
- **API Keys**: Use strong, unique keys for APIs
- **Network**: Run behind reverse proxy/load balancer in production

**See**: [docs/deployment/PRODUCTION_DEPLOYMENT.md](docs/deployment/PRODUCTION_DEPLOYMENT.md#security) for production checklist

---

## 📞 Support & Resources

### Documentation
- **Complete Index**: [docs/INDEX.md](docs/INDEX.md)
- **Setup Guides**: [docs/setup/](docs/setup/)
- **API Documentation**: [docs/api/](docs/api/)
- **Deployment**: [docs/deployment/](docs/deployment/)

### Tools & Scripts
- **API Registration**: `wso2-stack/apim/register_api.sh`
- **Database Init**: `scripts/init_*`
- **Verification**: [docs/guides/IMPLEMENTATION_VERIFICATION.md](docs/guides/IMPLEMENTATION_VERIFICATION.md)

### External Resources
- [WSO2 API Manager Documentation](https://apim.docs.wso2.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [React Documentation](https://react.dev/)

---

## ✅ Verification Checklist

Before going to production:

- [ ] All containers running successfully
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend API responding at http://localhost:8000/health
- [ ] APIM Admin accessible at https://localhost:9443/admin
- [ ] At least one API registered and published
- [ ] Database connections verified
- [ ] Default gateway configured
- [ ] SSL/TLS certificates configured
- [ ] Monitoring and logging enabled
- [ ] Backup procedures in place

**Detailed checklist**: [docs/guides/IMPLEMENTATION_VERIFICATION.md](docs/guides/IMPLEMENTATION_VERIFICATION.md)

---

## 📝 License

See [LICENSE](LICENSE) file for license information.

---

## 🎯 Next Steps

1. **Start the platform**: `docker-compose up -d`
2. **Access the dashboard**: http://localhost:3000
3. **Read the documentation**: Start with [docs/INDEX.md](docs/INDEX.md)
4. **Follow your role guide**: See [Getting Started by Role](#getting-started-by-role)

---

**Version**: 1.0  
**Last Updated**: April 24, 2026  
**Status**: ✅ Production Ready  

For detailed documentation, see [docs/INDEX.md](docs/INDEX.md)

