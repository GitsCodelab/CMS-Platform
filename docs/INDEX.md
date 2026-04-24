# CMS Platform Documentation Index

Welcome to the CMS Platform documentation. This section provides comprehensive guides for setup, deployment, and API management.

---

## 📖 Documentation Overview

### 🚀 [Setup & Installation](setup/)
Get started with the CMS Platform on new or existing servers.

| Guide | Purpose |
|-------|---------|
| **[APIM_SETUP_GUIDE.md](setup/APIM_SETUP_GUIDE.md)** | Complete WSO2 APIM 4.3.0 initialization with PostgreSQL database |
| **[SETUP_NEW_SERVER.md](setup/SETUP_NEW_SERVER.md)** | Step-by-step setup for new server environments |
| **[PHASE_1_IMPLEMENTATION_GUIDE.md](setup/PHASE_1_IMPLEMENTATION_GUIDE.md)** | Phase 1 implementation details and checklist |
| **[DATABASE_INIT_README.md](setup/DATABASE_INIT_README.md)** | Database initialization procedures |

---

### 🌐 [API Management](api/)
Register, manage, and publish APIs in APIM.

| Guide | Purpose |
|-------|---------|
| **[API_REGISTRATION_GUIDE.md](api/API_REGISTRATION_GUIDE.md)** | Complete guide for registering APIs with parameterized scripts |

---

### 🚢 [Production Deployment](deployment/)
Deploy the platform to production environments.

| Guide | Purpose |
|-------|---------|
| **[PRODUCTION_DEPLOYMENT.md](deployment/PRODUCTION_DEPLOYMENT.md)** | Production-grade setup, security, monitoring, and backup procedures |

---

### 📋 [Guides & Reference](guides/)
Additional guides and implementation details.

| Guide | Purpose |
|-------|---------|
| **[IMPLEMENTATION_VERIFICATION.md](guides/IMPLEMENTATION_VERIFICATION.md)** | Verify all components are functioning correctly |

---

### 🗂️ [Archived Documentation](archived/)
Legacy and historical documentation for reference.

| Document | Status |
|----------|--------|
| **CLAUDE.md** | Claude configuration notes |
| **CLAUDE.local.md** | Local Claude setup documentation |
| **ROOT_CAUSE_ISO_TO_API_GAP.md** | Root cause analysis (historical) |
| **WEBHOOK_vs_JPOS_PERSISTENCE_COMPARISON.md** | Webhook vs JPOS comparison (legacy) |
| **DOCUMENTATION_UPDATE_SUMMARY.md** | Previous documentation updates |

---

## 🎯 Quick Links by User Role

### 👤 New Users
1. Start with main [README.md](../README.md)
2. Follow [SETUP_NEW_SERVER.md](setup/SETUP_NEW_SERVER.md)
3. Review [APIM_SETUP_GUIDE.md](setup/APIM_SETUP_GUIDE.md) for APIM setup

### 👨‍💻 Developers
1. [API_REGISTRATION_GUIDE.md](api/API_REGISTRATION_GUIDE.md) - Register your APIs
2. [Backend API Documentation](../README.md#-backend---fastapi) - API endpoints
3. [IMPLEMENTATION_VERIFICATION.md](guides/IMPLEMENTATION_VERIFICATION.md) - Verify setup

### 🏗️ DevOps/SRE
1. [APIM_SETUP_GUIDE.md](setup/APIM_SETUP_GUIDE.md) - APIM infrastructure
2. [PRODUCTION_DEPLOYMENT.md](deployment/PRODUCTION_DEPLOYMENT.md) - Production setup
3. [Database procedures](setup/DATABASE_INIT_README.md) - Database administration

### 🔧 System Administrators
1. [PRODUCTION_DEPLOYMENT.md](deployment/PRODUCTION_DEPLOYMENT.md) - Server setup
2. [SETUP_NEW_SERVER.md](setup/SETUP_NEW_SERVER.md) - New server initialization
3. [APIM_SETUP_GUIDE.md](setup/APIM_SETUP_GUIDE.md) - APIM administration

---

## 📐 Architecture Documentation

For architecture diagrams and system design, see the main [README.md](../README.md#-architecture-overview)

---

## 🔄 Common Tasks

### Register a New API
```bash
bash wso2-stack/apim/register_api.sh \
  --name "My API" \
  --context "/api/myapi" \
  --backend "http://backend:8000/endpoint"
```
→ See [API_REGISTRATION_GUIDE.md](api/API_REGISTRATION_GUIDE.md) for complete guide

### Initialize APIM for First Time
```bash
# Follow steps in:
bash docs/setup/APIM_SETUP_GUIDE.md
```

### Deploy to Production
→ Follow [PRODUCTION_DEPLOYMENT.md](deployment/PRODUCTION_DEPLOYMENT.md)

---

## 📞 Support

For issues or questions:
1. Check [IMPLEMENTATION_VERIFICATION.md](guides/IMPLEMENTATION_VERIFICATION.md) to verify setup
2. Review troubleshooting sections in relevant guides
3. Check archived docs for historical context

---

**Last Updated**: April 24, 2026  
**Documentation Version**: 1.0
