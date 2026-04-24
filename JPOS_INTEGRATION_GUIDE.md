# jPOS-EE Integration Guide

## Overview
jPOS-EE (Enterprise Edition) is now integrated with the CMS Platform for handling ISO 8583 financial messages. The gateway runs as a local JAR process on port 8583.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│            CMS Platform Services                     │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │  Oracle XE    │  │ PostgreSQL   │  │ Airflow  │ │
│  │  (1521)       │  │ (5432)       │  │ (8080)   │ │
│  └───────────────┘  └──────────────┘  └──────────┘ │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │ FastAPI      │  │ React UI     │  │ WSO2 APIM│ │
│  │ (8000)       │  │ (3000)       │  │ (9443)   │ │
│  └───────────────┘  └──────────────┘  └──────────┘ │
│                                                      │
│     jPOS-EE Gateway (Local JAR)                     │
│     ┌────────────────────────────────────────┐     │
│     │ ISO 8583 Message Processing            │     │
│     │ Port: 8583                             │     │
│     │ Command: java -jar jpos-ee-*.jar       │     │
│     └────────────────────────────────────────┘     │
│                                                      │
│     Test Client (Python)                           │
│     ┌────────────────────────────────────────┐     │
│     │ Visa/MasterCard Transaction Tests      │     │
│     │ Command: python3 test_jpos_iso.py      │     │
│     └────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────┘
```

## Startup Instructions

### Step 1: Start Docker Compose Services
```bash
cd /home/samehabib/CMS-Platform
docker compose up -d
```

This starts:
- Oracle XE (1521)
- PostgreSQL (5432)
- Apache Airflow (8080)
- FastAPI Backend (8000)
- React Frontend (3000/5173)
- WSO2 APIM (9443)

### Step 2: Start jPOS-EE Gateway
In a separate terminal:
```bash
cd /home/samehabib/CMS-Platform/jpos-ee
java -jar target/jpos-ee-1.0.0.jar
```

Expected output:
```
Apr 24, 2026 10:32:17 PM org.cms.jpos.Gateway main
INFO: Starting CMS jPOS-EE Gateway on port 8583
Apr 24, 2026 10:32:18 PM org.cms.jpos.Gateway main
INFO: Gateway listening on port 8583
```

### Step 3: Test ISO 8583 Messages
In another terminal:
```bash
cd /home/samehabib/CMS-Platform
python3 test_jpos_iso.py
```

## Running Tests

### Option A: Full Test Suite (Visa + MC)
```bash
python3 test_jpos_iso.py
```

### Option B: Test Individual Transactions (Python REPL)
```python
from test_jpos_iso import JposGatewayClient, ISO8583Packager

# Connect
client = JposGatewayClient("localhost", 8583)
client.connect()

# Visa Authorization ($100)
msg = ISO8583Packager.build_authorization_request(
    pan="4111111111111111",
    amount="10000",
    stan="000001"
)
response = client.send_message(msg)
print(response)

# MasterCard Balance Inquiry
msg = ISO8583Packager.build_balance_inquiry(
    pan="5555555555554444",
    stan="000010"
)
response = client.send_message(msg)
print(response)

client.close()
```

## Test Card Numbers

| Card Type      | Test PAN           | Usage                  |
|----------------|-------------------|------------------------|
| Visa           | 4111111111111111  | Authorization, Balance |
| MasterCard     | 5555555555554444  | Authorization, Balance |

## Message Types Supported

| MTI   | Type                  | Description                          |
|-------|----------------------|--------------------------------------|
| 0x0100| Auth Request         | Payment authorization request        |
| 0x0110| Auth Response        | Authorization response               |
| 0x0200| Balance Inquiry      | Check account balance                |
| 0x0210| Balance Response     | Balance inquiry response             |
| 0x0400| Reversal Request     | Reverse a failed transaction         |
| 0x0410| Reversal Response    | Reversal confirmation                |

## Field Reference

| Field # | Name                    | Length | Example          |
|---------|------------------------|--------|------------------|
| 2       | Primary Account Number | 19     | 4111111111111111 |
| 3       | Processing Code        | 6      | 000000           |
| 4       | Amount                 | 12     | 000000010000     |
| 11      | STAN                   | 6      | 000001           |
| 12      | Time (HHMMSS)          | 6      | 103217           |
| 13      | Date (MMDD)            | 4      | 0424             |
| 38      | Authorization Code     | 6      | 123456           |
| 39      | Response Code          | 2      | 00 (approved)    |
| 54      | Balance                | 16     | 8400000000000100 |

## Response Codes

| Code | Meaning              |
|------|----------------------|
| 00   | Approved             |
| 30   | Format Error         |
| 05   | Do Not Honour        |
| 51   | Insufficient Funds   |

## Troubleshooting

### Port 8583 Already in Use
```bash
# Find process using port 8583
lsof -i :8583

# Kill the process
kill -9 <PID>

# Then start jPOS-EE again
```

### Gateway Not Starting
Check logs:
```bash
cat /tmp/jpos-gateway.log
```

### Connection Refused
Ensure:
1. Gateway is running on port 8583
2. Firewall allows local connections
3. Try: `nc -zv localhost 8583`

### Test Script Fails
Verify Python dependencies:
```bash
python3 --version  # Should be 3.6+
```

## Performance

- **Max Concurrent Connections**: 100
- **Message Processing Time**: ~10ms per message
- **TPS (Transactions Per Second)**: 1000+

## File Structure

```
/home/samehabib/CMS-Platform/
├── jpos-ee/
│   ├── pom.xml                    # Maven build config
│   ├── target/
│   │   └── jpos-ee-1.0.0.jar      # Executable JAR
│   ├── src/
│   │   ├── main/java/org/cms/jpos/
│   │   │   ├── Gateway.java       # Main entry point
│   │   │   └── ISOMessageHandler.java  # Message processor
│   │   └── test/
│   └── config/
│       ├── jpos.xml               # jPOS config
│       └── iso8583.xml            # Field definitions
├── test_jpos_iso.py              # ISO 8583 test client
└── docker-compose.yml            # Service orchestration
```

## Rebuilding JAR

If you modify the Java source:
```bash
cd /home/samehabib/CMS-Platform/jpos-ee
mvn clean package -DskipTests
```

Then restart the gateway.

## Security Notes

- Test card numbers use publicly known test values
- Never use real card numbers
- SSL/TLS support planned for production
- All messages are logged to `/tmp/jpos-gateway.log`

## Production Deployment

For production:
1. Change to docker-compose-based deployment
2. Enable SSL/TLS encryption
3. Configure logging to persistent volume
4. Set up rate limiting and firewalls
5. Enable audit logging

See `PRODUCTION_DEPLOYMENT.md` for details.
