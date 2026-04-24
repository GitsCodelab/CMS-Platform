# API Management & Registration

This directory contains guides for API management in WSO2 APIM.

## 📚 Available Guides

### API_REGISTRATION_GUIDE.md
**Complete guide for registering and managing APIs**

Covers:
- Quick 30-second API registration
- Parameterized script usage
- Manual REST API procedures
- API lifecycle management (Publish, Update, Delete)
- Batch registration
- Troubleshooting

**Key Features:**
- ✅ Parameter reference table
- ✅ 4 detailed real-world examples
- ✅ API publishing procedures
- ✅ Testing and subscription steps
- ✅ Error handling

---

## 🎯 Quick Actions

### Register a New API
```bash
bash ../../wso2-stack/apim/register_api.sh \
  --name "My API" \
  --context "/api/myapi" \
  --backend "http://backend:8000/endpoint"
```

### List All Registered APIs
```bash
curl -s -k https://localhost:9443/api/am/publisher/v4/apis \
  -u admin:admin | python3 -m json.tool
```

### Get API Details
```bash
curl -s -k https://localhost:9443/api/am/publisher/v4/apis/{API_ID} \
  -u admin:admin | python3 -m json.tool
```

---

## 📖 Related Documentation

- **Setup**: See [../setup/APIM_SETUP_GUIDE.md](../setup/APIM_SETUP_GUIDE.md) for APIM initialization
- **Production**: See [../deployment/PRODUCTION_DEPLOYMENT.md](../deployment/PRODUCTION_DEPLOYMENT.md) for production API management
- **Main README**: [../../README.md](../../README.md#-wso2-api-manager-apim)

---

**For complete documentation index**: See [../INDEX.md](../INDEX.md)
