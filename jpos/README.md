# jPOS (Java POS) Setup

jPOS is a high-performance, enterprise-grade framework for building payment systems and ISO 8583 message processors.

## Overview

This jPOS setup provides:
- **ISO 8583 Server**: Handles payment card transactions
- **Message Processing**: Parse and process financial messages
- **Logger**: Detailed transaction logging
- **Q2 Container**: Modular deployment platform

## Quick Start

### Prerequisites

- Docker and Docker Compose running
- PostgreSQL and backend services started

### Starting jPOS

```bash
docker compose up cms-jpos
```

This will:
1. Download pre-built jPOS v2.1.8
2. Deploy configuration files
3. Start ISO 8583 server on port 5000

### Access jPOS

**ISO 8583 Server**: `localhost:5000`
- Protocol: ASCII Channel with ISO87A Packager
- Default mode: Server listening for incoming connections

## Configuration

### Directory Structure

```
jpos/
├── Dockerfile           # Multi-stage build (downloads pre-built jPOS)
├── deploy/             # Q2 deployment descriptors
│   ├── 00_logger.xml   # Logging configuration
│   └── 10_q2.xml       # ISO server configuration
├── config/             # Custom configurations
├── jpos-src/           # (optional) Custom source code
└── lib/                # (optional) Additional libraries
```

### Key Configuration Files

#### `deploy/10_q2.xml` - ISO Server Config

```xml
<q2>
    <server class="org.jpos.iso.ISOServer" name="iso-server" logger="Q2">
        <attr name="port" type="java.lang.Integer">5000</attr>
        <channel class="org.jpos.iso.channel.ASCIIChannel"
                 packager="org.jpos.iso.packager.ISO87APackager"/>
    </server>
</q2>
```

- **Port**: 5000 (ISO 8583 listener)
- **Channel Type**: ASCIIChannel (text-based messaging)
- **Packager**: ISO87APackager (handles ISO 8583 format)

#### `deploy/00_logger.xml` - Logging Config

- **Log File**: `log/q2.log`
- **Max Size**: 10 MB per file
- **Backups**: 10 rotated log files

## Docker Integration

### Service Dependencies

```yaml
cms-jpos:
  depends_on:
    - cms-backend      # REST API for transaction processing
  ports:
    - "5000:5000"      # ISO 8583 port
```

### Network

- Connected to `cms-platform-net` bridge network
- Can reach:
  - `cms-backend:8000` - CMS API
  - `cms-postgresql:5432` - Database
  - `cms-oracle-xe:1521` - Oracle DB

## Usage Examples

### Testing ISO Connection

```bash
# Check if jPOS is running
docker ps | grep cms-jpos

# View logs
docker logs -f cms-jpos

# Execute commands inside container
docker exec cms-jpos ls -la /opt/jpos/dist/
```

### Adding Custom Message Processors

1. Create processor class in `config/`
2. Register in `deploy/` XML file
3. Restart container: `docker restart cms-jpos`

### Checking ISO Server Status

```bash
# Connect and test (if test client available)
nc -zv localhost 5000
```

## Integration with CMS Platform

### With Backend API

The jPOS server can:
1. Receive ISO 8583 messages on port 5000
2. Parse and validate transactions
3. Forward to `cms-backend:8000` for processing
4. Store results in PostgreSQL

### Payment Flow

```
Card Terminal
    ↓
ISO 8583 Message (port 5000)
    ↓
jPOS Server
    ↓
CMS Backend (API)
    ↓
PostgreSQL / Oracle
```

## Troubleshooting

### Container fails to start
```bash
# Check Docker build logs
docker compose build --no-cache cms-jpos

# View startup errors
docker logs cms-jpos
```

### Port already in use
```bash
# Find what's using port 5000
lsof -i :5000

# Or change port in 10_q2.xml
```

### jPOS download fails (SSL error)
- The Dockerfile includes SSL workaround
- If it fails, manually download from: https://github.com/jpos/jPOS/releases/download/v2.1.8/jPOS-2.1.8.zip
- Extract to `jpos/` and update Dockerfile

### No logs appearing
```bash
# Verify log directory exists
docker exec cms-jpos ls -la /opt/jpos/dist/log/

# Check permissions
docker exec cms-jpos chmod 777 /opt/jpos/dist/log/
```

## Performance Tuning

### Increase JVM Memory

Edit docker-compose.yml:
```yaml
environment:
  - JAVA_OPTS=-Xmx1024m -Xms512m
```

### Optimize for High Volume

1. Increase thread pools in Q2 config
2. Enable message batching
3. Optimize ISO packager settings

## Production Considerations

1. **Use HSM (Hardware Security Module)** for key management
2. **Enable TLS** for connections (update to SSLChannel)
3. **Monitor Performance** - Set up metrics collection
4. **Implement Failover** - Run multiple jPOS instances
5. **Audit Logging** - Enable detailed transaction logging
6. **Rate Limiting** - Prevent transaction flooding

## Documentation

- [jPOS Official Docs](https://jpos.org/doc)
- [ISO 8583 Standard](https://en.wikipedia.org/wiki/ISO_8583)
- [Q2 Container Guide](https://jpos.org/doc/javadoc/)

## Support & Resources

- GitHub: https://github.com/jpos/jPOS
- Community: https://groups.io/g/jpos
- Issues: https://github.com/jpos/jPOS/issues
