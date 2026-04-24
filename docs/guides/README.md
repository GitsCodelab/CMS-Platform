# Guides & Reference

This directory contains additional guides and implementation verification procedures.

## 📚 Available Guides

### IMPLEMENTATION_VERIFICATION.md
**Verify all components are functioning correctly**

Covers:
- Component verification procedures
- Health checks
- Integration testing
- Performance validation
- Troubleshooting steps

**Use this to:**
- ✅ Verify fresh installation
- ✅ Test after updates
- ✅ Diagnose issues
- ✅ Confirm integrations working

---

## 🎯 Verification Checklist

Before going live:

- [ ] All containers running (`docker compose ps`)
- [ ] Frontend responsive (http://localhost:3000)
- [ ] Backend API healthy (http://localhost:8000/health)
- [ ] Databases accessible
- [ ] APIM responding (https://localhost:9443)
- [ ] All APIs registered and published
- [ ] Airflow running (http://localhost:8080)

---

## 📖 Related Documentation

- **Setup**: See [../setup/SETUP_NEW_SERVER.md](../setup/SETUP_NEW_SERVER.md)
- **APIM**: See [../api/API_REGISTRATION_GUIDE.md](../api/API_REGISTRATION_GUIDE.md)
- **Deployment**: See [../deployment/PRODUCTION_DEPLOYMENT.md](../deployment/PRODUCTION_DEPLOYMENT.md)
- **Main README**: [../../README.md](../../README.md)

---

**For complete documentation index**: See [../INDEX.md](../INDEX.md)
