# CMS Platform Architecture Documentation

**Version**: 1.1  
**Date**: April 24, 2026  
**Status**: ✅ Updated with jPOS-EE Integration

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Service Architecture](#service-architecture)
3. [Component Descriptions](#component-descriptions)
4. [Data Flow](#data-flow)
5. [Network Topology](#network-topology)
6. [Technology Stack](#technology-stack)
7. [Scalability & Performance](#scalability--performance)
8. [Security Architecture](#security-architecture)

---

## System Overview

The CMS Platform is an enterprise-grade solution composed of multiple microservices designed to handle:

- **API Lifecycle Management** (WSO2 APIM)
- **ISO 8583 Financial Message Processing** (jPOS-EE)
- **RESTful API Services** (FastAPI)
- **Workflow Orchestration** (Apache Airflow)
- **Data Management** (Oracle, PostgreSQL)
- **User Interface** (React)

### Key Characteristics

- **Microservices Architecture**: Independent, loosely coupled services
- **Docker Containerization**: Consistent deployment across environments
- **Network Isolation**: Bridge network (`cms-platform-net`) for secure inter-service communication
- **Scalable Design**: Each service can be scaled independently
- **High Availability Ready**: Prepared for multi-node deployment

---

## Service Architecture

### High-Level System Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          USERS & APPLICATIONS                              │
│  (Browsers, Mobile Apps, Third-party Systems, Payment Terminals)            │
└──────────────────────────┬─────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼──────────────────┐
        │ HTTP/HTTPS      │ ISO 8583         │
        │ (JSON/REST)     │ (Binary Protocol)│
        │                 │                  │
┌───────▼──────────────────┐  ┌─────────────▼──────────────────┐
│  API Manager Gateway     │  │  ISO 8583 Gateway (jPOS-EE)    │
│  (WSO2 APIM 4.3.0)       │  │  (Financial Transactions)      │
│  :9443, :8280, :8243     │  │  :8583                         │
│                          │  │                                │
│ • API Lifecycle Mgmt     │  │ • Auth Requests                │
│ • Rate Limiting          │  │ • Balance Inquiry              │
│ • Authentication         │  │ • Reversals                    │
│ • Policy Enforcement     │  │ • PIN Changes                  │
│ • Analytics              │  │ • Transaction Handling         │
└────────┬─────────────────┘  └─────────────┬──────────────────┘
         │                                  │
         └──────────────────┬───────────────┘
                            │
                            ▼
         ┌──────────────────────────────────┐
         │  Backend API Layer (FastAPI)     │
         │  :8000                           │
         │                                  │
         │ • REST Endpoints                 │
         │ • Business Logic                 │
         │ • Data Integration               │
         │ • Error Handling                 │
         └──┬─────┬──────────────┬────┬─────┘
            │     │              │    │
    ┌───────▼──┬──▼──────┬──────▼┐   │
    │          │         │      │    │
    ▼          ▼         ▼      ▼    ▼
  ┌──────┐ ┌─────────┐ ┌──────┐┌────┐┌──────────┐
  │Oracle│ │PostgreSQL│ │Airflow││Redis││Cache     │
  │ DB   │ │   DWH    │ │:8080  ││:6379││/Config   │
  │:1521 │ │  :5432   │ │       │└────┘└──────────┘
  └──────┘ └─────────┘ └──────┘
  (Transact.)(Analytics)(Orchestr.)
```

---

## Component Descriptions

### 1. Frontend Layer

**Technology**: React 18+  
**Port**: 3000  
**Purpose**: User interface and client-side application

**Features**:
- Modern responsive UI with Tailwind CSS
- Real-time data visualization
- API consumption and integration
- State management
- Authentication handling

**API Communication**:
- Via WSO2 APIM Gateway (http://localhost:8280)
- REST endpoints with JSON payloads
- OAuth2 token-based authentication

---

### 2. API Gateway Layer

#### WSO2 API Manager (APIM) 4.3.0

**Ports**:
- Admin/Publisher: 9443 (HTTPS)
- API Gateway HTTP: 8280 (HTTP)
- API Gateway HTTPS: 8243 (HTTPS)

**Responsibilities**:
- API versioning and lifecycle management
- Rate limiting and throttling
- Authentication and authorization
- Request/response transformation
- API analytics and monitoring
- Policy enforcement

**Configuration**:
```
Gateway Name: Default
Type: Hybrid
HTTP Endpoint: http://localhost:8280
HTTPS Endpoint: https://localhost:8243
Database: PostgreSQL (wso2am)
```

**Registered APIs**:
- CMS Oracle Test API: `/cms/oracle`
- CMS PostgreSQL API: `/cms/postgres`
- Custom APIs (as registered)

---

### 3. ISO 8583 Gateway Layer

**Technology**: jPOS-EE (jPOS Enterprise Edition)  
**Port**: 8583  
**Purpose**: Financial transaction message processing

**Capabilities**:
- ISO 8583:2003 message handling
- Multiple transaction types:
  - Authorization (0x0100)
  - Balance Inquiry (0x0200)
  - Financial Transaction (0x0220)
  - Transaction Reversal (0x0400)
  - PIN Change (0x0600)
  - Logoff (0x0500)
  - Echo Test (0x0800)

**Architecture**:
```
ISO Message Handler
├── Message Parsing
├── Field Validation
├── Business Logic Processing
├── Response Generation
└── Logging & Audit
```

**Test Coverage**:
- 9 comprehensive test cases
- Different business scenarios
- Stress testing (multiple concurrent messages)
- Error handling verification

---

### 4. Backend API Layer

**Technology**: FastAPI (Python)  
**Port**: 8000  
**Purpose**: RESTful API and business logic

**Core Features**:
- Async request handling
- Multiple database integration
- OpenAPI/Swagger documentation
- Health check endpoints
- Comprehensive error handling
- Request validation and transformation

**Main Endpoints**:
- `/health` - System health check
- `/oracle/*` - Oracle database operations
- `/postgres/*` - PostgreSQL operations
- `/orders/*` - Order management
- `/docs` - Swagger UI
- `/redoc` - ReDoc documentation

**Database Connectivity**:
- Oracle XE (Primary transactional)
- PostgreSQL (DWH and APIM)
- Connection pooling for performance

---

### 5. Workflow Orchestration

**Technology**: Apache Airflow  
**Port**: 8080  
**Purpose**: Scheduled jobs and data pipelines

**Capabilities**:
- DAG (Directed Acyclic Graph) based workflows
- Scheduled task execution
- Multi-database operations
- Data validation and reconciliation
- Error handling and retries
- Monitoring and alerting

**Key Workflows**:
- Data synchronization between databases
- ETL (Extract, Transform, Load) processes
- Report generation
- Data quality checks

---

### 6. Database Layer

#### Oracle Database (XE)

**Port**: 1521  
**Purpose**: Primary transactional database

**Contents**:
- Master tables
- Transaction data
- Business entities
- Real-time data

**Connection Details**:
```
Service Name: xepdb1
Username: MAIN
Password: main123 (change in production)
```

#### PostgreSQL Database

**Port**: 5432  
**Purpose**: 
- APIM configuration and metadata (wso2am database)
- Data warehouse for analytics

**Databases**:
- `wso2am` - APIM schema
- `recon_dwh` - Analytics and reporting

**Connection Details**:
```
Username: postgres
Password: postgres (change in production)
```

---

## Data Flow

### 1. HTTP/REST API Flow

```
User Request
    ↓
Frontend (React)
    ↓ HTTP/HTTPS
WSO2 APIM Gateway
    ├─ Authentication Check
    ├─ Rate Limiting Check
    ├─ Policy Enforcement
    └─ Request Routing
         ↓
Backend API (FastAPI)
    ├─ Request Validation
    ├─ Business Logic Processing
    └─ Database Operation
         ↓
    ┌────────────────┬──────────────┬──────────┐
    ▼                ▼              ▼          ▼
Oracle DB      PostgreSQL     Airflow      Cache
    ↓                ↓              ↓          ↓
Response Generation
    ↓
Response Transformation (APIM)
    ↓
Frontend Rendering
    ↓
User Interface Update
```

### 2. ISO 8583 Message Flow

```
Terminal/ATM/POS
    ↓ ISO 8583 Binary Protocol
jPOS-EE Gateway (Port 8583)
    ├─ Message Parsing
    ├─ Field Extraction
    └─ Message Type Routing
         ↓
ISOMessageHandler
    ├─ Authorization Handler
    ├─ Balance Handler
    ├─ Financial Transaction Handler
    ├─ Reversal Handler
    ├─ PIN Change Handler
    └─ etc.
         ↓
    ┌────────────────┬──────────────┐
    ▼                ▼              ▼
Oracle DB      PostgreSQL       Logging
    ↓                ↓              ↓
Response Generation
    ↓
ISO Message Formatting
    ↓
Terminal/ATM/POS Response
```

### 3. Workflow/ETL Flow

```
Scheduled Trigger (Airflow)
    ↓
DAG Execution
    ├─ Extract
    │  ├─ Oracle Data Pull
    │  └─ PostgreSQL Query
    ├─ Transform
    │  ├─ Data Validation
    │  ├─ Aggregation
    │  └─ Enrichment
    └─ Load
         ├─ PostgreSQL Write
         ├─ Oracle Update
         └─ Cache Refresh
              ↓
Monitoring & Alerting
```

---

## Network Topology

### Docker Network

```
┌─────────────────────────────────────────────────┐
│    Docker Bridge Network: cms-platform-net      │
│                                                 │
│  ┌────────────────────────────────────────┐    │
│  │         Service DNS Resolution         │    │
│  ├────────────────────────────────────────┤    │
│  │ cms-frontend:3000                      │    │
│  │ cms-backend:8000                       │    │
│  │ cms-apim:9443, 8280, 8243             │    │
│  │ cms-jpos-ee:8583                       │    │
│  │ cms-postgresql:5432                    │    │
│  │ cms-oracle-xe:1521                     │    │
│  │ airflow-webserver:8080                 │    │
│  └────────────────────────────────────────┘    │
│                                                 │
└─────────────────────────────────────────────────┘
         │
    ┌────┴─────────────┐
    ▼                  ▼
Host Ports       External Network
3000, 8000       (Load Balancer,
8080, 8280,      Firewalls,
8243, 8583,      Proxies,
9443, 1521,      etc.)
5432
```

### Service Communication

**Direct Container DNS Names** (within network):
- `cms-frontend` → Frontend React app
- `cms-backend` → Backend FastAPI service
- `cms-apim` → WSO2 API Manager
- `cms-jpos-ee` → jPOS-EE gateway
- `cms-postgresql` → PostgreSQL database
- `cms-oracle-xe` → Oracle database
- `airflow-webserver` → Apache Airflow

**Example Inter-service Communication**:
```
Backend to Oracle:
curl http://cms-oracle-xe:1521

Backend to PostgreSQL:
psql -h cms-postgresql -U postgres

Backend to Airflow:
curl http://airflow-webserver:8080/api

APIM to Backend:
http://cms-backend:8000
```

---

## Technology Stack

### Frontend
- **Framework**: React 18+
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios/Fetch API
- **Build Tool**: Vite
- **Package Manager**: npm/yarn

### Backend
- **Framework**: FastAPI (Python 3.8+)
- **ASGI Server**: Uvicorn
- **ORM**: SQLAlchemy (if used)
- **Database Drivers**: cx_Oracle, psycopg2
- **Task Queue**: Celery (optional)

### API Gateway
- **Platform**: WSO2 API Manager 4.3.0
- **Database**: PostgreSQL
- **Features**: CORS, OAuth2, API Versioning

### ISO Message Gateway
- **Framework**: jPOS Enterprise Edition
- **Language**: Java 11+
- **Build Tool**: Maven
- **Protocol**: ISO 8583:2003

### Workflow Orchestration
- **Tool**: Apache Airflow 2.x
- **Executor**: LocalExecutor / CeleryExecutor
- **Database**: PostgreSQL
- **Scheduler**: SequentialScheduler / CeleryScheduler

### Databases
- **Transactional**: Oracle Database XE
- **Analytics/Config**: PostgreSQL 15.x
- **Caching**: Redis (optional)

### DevOps/Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Version Control**: Git
- **CI/CD**: GitHub Actions (optional)

---

## Scalability & Performance

### Horizontal Scaling

**Services that can be scaled**:
1. **Frontend** - Multiple instances behind load balancer
2. **Backend API** - Multiple instances with load balancing
3. **APIM Gateway** - Multiple nodes with clustering
4. **jPOS-EE** - Multiple instances for high transaction volume
5. **Airflow Workers** - Scale out workers for more parallelism

**Example Scaling Configuration**:
```yaml
services:
  cms-backend:
    deploy:
      replicas: 3
  cms-jpos-ee:
    deploy:
      replicas: 2
```

### Vertical Scaling

**Resource Allocation**:
```
Default (Development):
- Frontend: 256MB
- Backend: 512MB
- APIM: 1GB
- jPOS-EE: 512MB
- PostgreSQL: 1GB
- Oracle: 2GB

Production (Recommended):
- Frontend: 512MB - 1GB
- Backend: 1GB - 2GB
- APIM: 2GB - 4GB
- jPOS-EE: 1GB - 2GB
- PostgreSQL: 2GB - 4GB
- Oracle: 4GB - 8GB
```

### Performance Optimization

**Backend Optimization**:
- Connection pooling (database)
- Request caching
- Asynchronous processing
- Database query optimization

**APIM Optimization**:
- API caching
- Response compression
- Connection pooling
- Message queue buffering

**Database Optimization**:
- Index optimization
- Query tuning
- Partitioning strategy
- Backup/recovery procedures

---

## Security Architecture

### Network Security

```
┌──────────────────────────────────────────┐
│         External Network/Internet         │
│  (Attackers, Network Threats)             │
└────────────────┬─────────────────────────┘
                 │
        ┌────────▼────────┐
        │  Load Balancer  │
        │  (if deployed)  │
        └────────┬────────┘
                 │ HTTPS/TLS
        ┌────────▼─────────────┐
        │  Reverse Proxy       │
        │  (WAF Rules)         │
        └────────┬─────────────┘
                 │ HTTPS/TLS
        ┌────────▼──────────────────────────┐
        │   Docker Host Network              │
        │   ┌─────────────────────────────┐  │
        │   │  Docker Bridge Network      │  │
        │   │  (cms-platform-net)         │  │
        │   │  - All services in network  │  │
        │   │  - No direct external access│  │
        │   └─────────────────────────────┘  │
        └────────────────────────────────────┘
```

### Authentication & Authorization

**APIM Security**:
- OAuth2 authentication
- API Key validation
- User roles and permissions
- Token expiration

**Backend Security**:
- Request validation
- Authorization headers
- Role-based access control (RBAC)
- Data encryption at rest

**Database Security**:
- Strong passwords
- User authentication
- SQL injection prevention
- Data encryption (recommended)

### Data Protection

**In Transit**:
- HTTPS/TLS encryption
- SSL certificates
- Encrypted message headers

**At Rest**:
- Database encryption (recommended)
- Configuration file protection
- Secret management
- Backup encryption

---

## Deployment Architectures

### Development Setup (Current)

```
Single Host / Docker Compose
│
├─ Frontend Container
├─ Backend Container
├─ APIM Container
├─ jPOS-EE Container
├─ PostgreSQL Container
├─ Oracle Container
└─ Airflow Container
```

### Production Setup (Recommended)

```
Multi-Host / Kubernetes
│
├─ Web Tier (Load Balancer)
│  ├─ Frontend (CDN)
│  └─ Reverse Proxy (Nginx/HAProxy)
│
├─ API Tier
│  ├─ APIM Cluster (3+ nodes)
│  └─ Backend API Pods (3+ replicas)
│
├─ Message Processing Tier
│  └─ jPOS-EE Cluster (2+ nodes)
│
├─ Data Tier
│  ├─ Oracle RAC (High Availability)
│  └─ PostgreSQL Cluster
│
└─ Orchestration Tier
   └─ Airflow (Distributed)
```

---

## Monitoring & Observability

### Key Metrics to Monitor

1. **Application Metrics**:
   - Request latency (p50, p95, p99)
   - Error rate
   - Throughput (requests/sec)
   - Resource utilization

2. **Infrastructure Metrics**:
   - CPU usage
   - Memory consumption
   - Disk space
   - Network I/O

3. **Database Metrics**:
   - Query performance
   - Connection pool usage
   - Transactions per second
   - Replication lag

4. **Business Metrics**:
   - API success rate
   - Transaction volume
   - User activity
   - Revenue impact

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | Apr 24, 2026 | Added jPOS-EE architecture |
| 1.0 | Apr 1, 2026 | Initial architecture |

---

**Status**: ✅ Production Ready  
**Last Updated**: April 24, 2026  
**Maintainer**: CMS Platform Team
