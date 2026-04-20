# jPOS EE (Enterprise Edition) Setup

jPOS EE is the enterprise version of jPOS with advanced features for payment processing, including:
- Advanced message routing and transformation
- Batch processing and scheduling
- Enhanced transaction logging and audit
- Commercial support and SLAs
- Enterprise connectors and adapters

## Quick Start (Development Mode)

### 1. Using Provided Enterprise Binaries

If you have jPOS EE distribution:

```bash
# Copy jPOS EE JAR to lib folder
cp /path/to/jposee-*.jar jposee/lib/

# Copy enterprise configuration
cp /path/to/enterprise-config.xml jposee/config/

# Build and run
cd /path/to/CMS-Platform
docker compose build cms-jposee
docker compose up cms-jposee
```

### 2. Using Maven with Enterprise Credentials

If your organization has Maven Central access to jPOS EE:

```bash
# Update Dockerfile to use Maven Central coordinates
# Then build
docker compose build cms-jposee --no-cache
```

### 3. Development Mode (Base jPOS Fallback)

Without jPOS EE binaries, container starts with base jPOS:

```bash
docker compose build cms-jposee
docker compose up cms-jposee -d
```

## Directory Structure

```
jposee/
├── Dockerfile              # Multi-stage build for jPOS EE
├── .gitignore              # Exclude build artifacts
├── deploy/                 # XML configuration files
│   └── 00_logger.xml       # Logging configuration
├── config/                 # Enterprise configuration
│   ├── system.properties   # System settings
│   ├── channels.xml        # Channel definitions
│   └── connectors.xml      # Connector configurations
├── lib/                    # Enterprise JAR files (local)
│   ├── jposee-*.jar       # jPOS EE distribution
│   ├── connector-*.jar    # Enterprise connectors
│   └── *.jar              # Other dependencies
└── README.md              # This file
```

## Configuration Files

### deploy/00_logger.xml
Configures jPOS Q2 logging with rotation:
- Log file: `log/q2ee.log`
- Max size: 10MB
- Backup files: 10
- Auto-rotation enabled

## Container Ports

- **5000**: ISO 8583 Server (standard)
- **5001**: ISO 8583 Server (secondary/backup)

## Environment Setup

### Required for Enterprise

1. **jPOS EE Distribution** (commercial)
   - Download from jPOS.org (with valid license)
   - Place JAR in `lib/` folder

2. **Enterprise Configuration**
   - Custom channel definitions
   - Connector configurations
   - Security policies
   - Place in `config/` folder

3. **Deployment Bundles**
   - Custom message handlers
   - Business logic modules
   - Place XML in `deploy/` folder

### Optional

- Custom logging configuration
- Performance tuning parameters
- Security certificates

## Build & Run

### Build Container

```bash
cd /path/to/CMS-Platform

# Without cache (fresh build)
docker compose build cms-jposee --no-cache

# With cache (faster)
docker compose build cms-jposee
```

### Run Container

```bash
# Start jPOS EE (detached)
docker compose up cms-jposee -d

# View logs
docker logs cms-jposee
docker logs -f cms-jposee

# Stop container
docker compose stop cms-jposee

# Remove container
docker compose rm cms-jposee
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker logs cms-jposee | grep -i error

# Check if jPOS EE binaries are present
docker run -it cms-platform-cms-jposee ls -la dist/lib/

# Verify configuration
docker run -it cms-platform-cms-jposee cat dist/config/system.properties
```

### ClassNotFoundException

If you see `ClassNotFoundException: org.jpos.ee.*`:
1. Verify jPOS EE JAR is in `dist/lib/`
2. Check JAR is not corrupted: `jar -tf lib/jposee-*.jar | head`
3. Ensure all enterprise dependencies are included

### Performance Issues

1. Review `deploy/00_logger.xml` - reduce logging if needed
2. Check JVM settings in `bin/q2.sh` or `bin/q2ee`
3. Monitor logs: `docker logs cms-jposee | tail -100`

### Integration with Backend

jPOS EE connects to backend on port 8000:

```bash
# Test connectivity
docker exec cms-jposee nc -zv cms-backend 8000
```

## Enterprise Features

When using full jPOS EE, you get:

- ✅ Advanced message routing
- ✅ Batch processing
- ✅ Enhanced transaction audit trail
- ✅ Commercial connectors (BIN, NETS, etc.)
- ✅ Enterprise security features
- ✅ High availability clustering
- ✅ Commercial support

## Development Tips

1. **Custom Channels**: Add in `deploy/channels.xml`
2. **Custom Handlers**: Implement in `deploy/custom-handlers.xml`
3. **Logging**: Configure in `deploy/00_logger.xml`
4. **Performance**: Tune in JVM startup parameters

## Docker Compose Integration

Service is defined in `docker-compose.yml`:

```yaml
cms-jposee:
  build:
    context: ./jposee
    dockerfile: Dockerfile
  container_name: cms-jposee
  ports:
    - "5001:5000"      # ISO 8583 standard
    - "5002:5001"      # ISO 8583 secondary
  volumes:
    - ./jposee/log:/opt/jposee/dist/log
    - ./jposee/deploy:/opt/jposee/dist/deploy
    - ./jposee/config:/opt/jposee/dist/config
  networks:
    - cms-platform-net
  depends_on:
    - cms-postgresql
    - cms-backend
  environment:
    - JPOS_LOG_LEVEL=info
```

## Security Considerations

1. **Credentials**: Never commit credentials to git
2. **SSL/TLS**: Configure in `deploy/security.xml`
3. **Database Access**: Use environment variables for secrets
4. **Network**: Container only accessible via docker network

## License & Support

- jPOS EE requires commercial license
- Visit: https://jpos.org/
- Commercial support included with license

## Next Steps

1. Obtain jPOS EE distribution from jPOS.org
2. Copy JAR to `lib/` folder
3. Configure enterprise settings in `config/`
4. Build and test container
5. Deploy to production cluster

---

**Last Updated**: April 20, 2026  
**Status**: Ready for enterprise deployment
