# Phase 4: jPOS Configuration Guide

## Overview

Phase 4 creates the XML configuration files that wire the jPOS framework with the persistence layer. These files configure:

1. **01_iso_persist.xml** - TransactionManager with participant chain
2. **02_channel_config.xml** - ISO 8583 channel listener on port 5001

## Architecture

```
ISO 8583 Client (Port 5001)
        ↓
   ISOServer (Listener)
        ↓
   [ISO Message received]
        ↓
   Request Queue
        ↓
   TransactionManager
        ↓
   Participant Chain:
     1. PersistRequest → [Saves to DB, status=RECEIVED]
     2. [Business Processing Participants]
     3. UpdateResponse → [Updates DB, status=PROCESSED/FAILED]
        ↓
   Response Queue
        ↓
   ISO Client Response
```

## Configuration Files

### 01_iso_persist.xml - TransactionManager

**Purpose**: Define the participant chain for transaction processing

**Key Components**:

```xml
<transaction-manager class="org.jpos.transaction.TransactionManager">
  <participant class="org.cms.jposee.participant.PersistRequest" name="PersistRequest" />
  <participant class="org.cms.jposee.participant.UpdateResponse" name="UpdateResponse" />
</transaction-manager>
```

**Timeouts & Policies**:
- `abort-timeout`: 120 seconds - time before auto-abort
- `idle-timeout`: 300 seconds - maximum transaction lifetime
- `max-sessions`: 1000 - concurrent transactions allowed
- `max-retries`: 3 - retry failed transactions
- `retry-delay`: 1000ms - wait between retries

**Persistence Store**:
- Stores transactions to `target/tx.log` for recovery
- Allows restart recovery if node crashes

### 02_channel_config.xml - ISO Channel

**Purpose**: Configure the ISO 8583 listener on port 5001

**Key Components**:

```xml
<server class="org.jpos.iso.ISOServer" port="5001">
  <channel class="org.jpos.iso.ISOChannel">
    <packager class="org.jpos.iso.packager.GenericPackager"/>
  </channel>
  <request-listener transaction-manager="TransactionManager" queue="REQUEST"/>
  <response-sender response-queue="RESPONSE"/>
</server>
```

**Network Configuration**:
- Port: 5001 (ISO 8583 transaction port)
- Max clients: 100 simultaneous connections
- Socket timeout: 60 seconds
- Backlog: 50 pending connections

**PCI-DSS Compliance**:
- Captures peer IP address → `PEER_ADDRESS` in context
- Captures peer port → `PEER_PORT` in context
- Logs all transactions (configurable)
- Exception handling prevents crashes on bad messages

## Message Flow

### Step 1: Incoming Transaction
1. ISO 8583 client connects to port 5001
2. ISOServer accepts connection
3. Binary ISO message received

### Step 2: Queue & TransactionManager
1. Message placed in REQUEST queue
2. TransactionManager picks up message
3. Begins transaction processing

### Step 3: PersistRequest Participant (First)
1. Extracts ISO fields from raw message
2. **Masks PAN** for secure storage (PCI-DSS Req 3.2.1)
3. **Creates IsoTransaction** record with status=RECEIVED
4. **Stores raw request** for audit trail
5. **Captures IP/session** information
6. **Returns ISO_TXN_ID** to context

### Step 4: Business Processing (Middle Participants)
- Other participants process the transaction
- Business logic, validation, etc.
- (Not in scope for Phase 4 - covered in Phase 5)

### Step 5: UpdateResponse Participant (Last)
1. Receives transaction ID from context
2. Retrieves persisted transaction from database
3. **Extracts response fields** from processor
4. **Updates transaction** with response code, RRN, auth ID
5. **Determines status** from response code:
   - `00` → PROCESSED
   - `05` → DECLINED
   - Other → FAILED
6. **Stores raw response** message
7. **Creates audit trail entry** documenting the update
8. **Flags for compliance** verification

### Step 6: Response Sent Back
1. Response placed in RESPONSE queue
2. ResponseSender retrieves and sends to ISO client
3. Client receives response
4. Connection closed

## PCI-DSS Compliance Implementation

### Requirement 3.2.1 (PAN Protection)
✅ **Masked in PersistRequest**
- Format: `XXXXXX****1234` (first 6, last 4 visible)
- Used in all logs/audit trails
- Full PAN stored only if encrypted

### Requirement 10.1 (Logging)
✅ **Implemented at multiple points**
- ISOServer logs all connections
- Request logged: timestamp + ISO fields
- Response logged: timestamp + response code
- Audit table: immutable log of all changes

### Requirement 10.2 (User/IP Identification)
✅ **Captured during transaction**
- IP address: `ip_address` column (from PEER_ADDRESS)
- Session ID: `session_id` column (from channel context)
- User ID: `created_by` / `updated_by` columns
- Timestamp: `created_at` / `updated_at` (set by @PrePersist/@PreUpdate)

### Requirement 10.3 (Immutable Audit Trail)
✅ **iso_transactions_audit table**
- Records created for each update
- `created_at` NOT updatable (immutable)
- `id` auto-incremented (cannot be reused)
- ON DELETE CASCADE prevents orphaned records
- Fields logged: action, field_name, old_value, new_value, changed_by, ip_address, session_id, reason

## Integration Points

### TransactionManager ← ISOServer
```
02_channel_config.xml → <request-listener transaction-manager="TransactionManager"/>
01_iso_persist.xml → <transaction-manager name="TransactionManager"/>
```
The channel passes messages to the TransactionManager for processing.

### ISOServer ← Participants
```
PersistRequest: Saves initial transaction
UpdateResponse: Updates transaction with response
```
Both participants use repositories injected from Spring (in Phase 5).

### Database ← Repositories
```
IsoTransactionRepository → iso_transactions table
IsoTransactionAuditRepository → iso_transactions_audit table
```
Repositories execute JPA queries via EntityManager.

## Deployment Architecture

```
jPOS Runtime (Main Process)
├── TransactionManager (01_iso_persist.xml)
│   ├── PersistRequest Participant
│   └── UpdateResponse Participant
├── ISOServer (02_channel_config.xml)
│   ├── Channel Listener (port 5001)
│   ├── Request Queue
│   └── Response Queue
└── EntityManager (persistence.xml)
    └── PostgreSQL Database
        ├── iso_transactions (main table)
        └── iso_transactions_audit (audit trail)
```

## Configuration Loading

In jPOS, these XML files are loaded via the Q2 service loader:

```bash
# File structure
jpos-ee/
└── src/main/resources/
    ├── META-INF/
    │   └── persistence.xml (Hibernate configuration)
    ├── 01_iso_persist.xml (TransactionManager)
    └── 02_channel_config.xml (ISOServer)

# At startup, Q2 discovers and loads:
# 1. persistence.xml → EntityManagerFactory initialized
# 2. 01_iso_persist.xml → TransactionManager created
# 3. 02_channel_config.xml → ISOServer starts listening on 5001
```

## Testing the Configuration

### Manual Test (Phase 5+)
```bash
# Send test ISO message to port 5001
# Observe:
# 1. Transaction persisted (SELECT * FROM iso_transactions)
# 2. Status: RECEIVED (PersistRequest executed)
# 3. Response received by client (port 5001)
# 4. Status: PROCESSED (UpdateResponse executed)
# 5. Audit trail created (SELECT * FROM iso_transactions_audit)
```

### Expected Logs
```
2026-04-21 21:15:00 [INFO] TransactionManager started
2026-04-21 21:15:01 [INFO] ISOServer listening on port 5001
2026-04-21 21:15:05 [INFO] Connection from 127.0.0.1:54321
2026-04-21 21:15:05 [INFO] Transaction persisted: txnId=1001 STAN=123456 Amount=100.00
2026-04-21 21:15:06 [INFO] Transaction updated: txnId=1001 status=PROCESSED responseCode=00
```

## Next Steps (Phase 5)

Phase 5 will create:
1. **Unit Tests** - Test individual components
2. **Integration Tests** - Test participant chain end-to-end
3. **Load Tests** - Verify 1000+ txns/sec capability
4. **Test fixtures** - Sample ISO messages

These tests will validate:
- ✅ PersistRequest saves transactions
- ✅ UpdateResponse updates correctly
- ✅ Audit trail is immutable
- ✅ PAN masking works
- ✅ Response codes mapped to status correctly
- ✅ Performance requirements met

## Configuration Summary

| Item | Value | Purpose |
|------|-------|---------|
| Port | 5001 | ISO 8583 listener port |
| Max Clients | 100 | Concurrent connections |
| Max Sessions | 1000 | Concurrent transactions |
| Abort Timeout | 120s | Auto-abort if no response |
| Idle Timeout | 300s | Max transaction lifetime |
| Max Retries | 3 | Failed transaction retries |
| Retry Delay | 1000ms | Wait between retries |
| Socket Timeout | 60s | Socket idle timeout |
| Response Timeout | 30s | Response send timeout |

## Troubleshooting

### Issue: Port 5001 already in use
**Solution**: Change port in 02_channel_config.xml
```xml
<property name="port" value="5002"/>
```

### Issue: TransactionManager not found
**Solution**: Ensure 01_iso_persist.xml is loaded before 02_channel_config.xml

### Issue: High latency
**Solution**: Increase thread pool size
```xml
<property name="thread-pool-size" value="30"/>
```

### Issue: Transaction timeout
**Solution**: Increase abort-timeout in 01_iso_persist.xml
```xml
<property name="abort-timeout" value="300s"/>
```

---

**Configuration Status**: ✅ Complete
**Build Status**: ✅ SUCCESS (all classes compile)
**Next Phase**: Phase 5 - Unit & Integration Tests
