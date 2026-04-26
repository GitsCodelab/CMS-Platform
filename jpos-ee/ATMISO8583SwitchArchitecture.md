# 🏗️ ATM ISO8583 Switch Architecture (jPOS + Python)

## 🎯 Overview

This project implements a **hybrid ATM switch architecture** combining:

* **Java (jPOS EE)** → ISO8583 gateway & protocol handling
* **Python** → transaction lifecycle & business logic (switch engine)
* **Database (upcoming)** → persistence & source of truth

---

# 🧠 Architecture Overview

```text
ATM / POS
   ↓
Java Gateway (jPOS)
   ↓
Python Switch Engine
   ↓
Database (Persistence)
   ↓
Core Banking / External Systems
```

---

# 🧩 Components

## 🟡 Java Layer (jPOS EE)

### Gateway

* TCP socket server
* Accepts ATM/POS connections
* Sends/receives ISO8583 messages

### ISO Handler

* ISO8583 parsing & packing
* Field validation
* MAC validation (ANSI X9.19)
* DUKPT validation
* Replay protection

### Packager (iso87.xml)

* Defines ISO8583 structure
* Field formats, lengths, encoding

### Config

* MAC keys
* BDK keys
* Timeout configs

---

## 🟢 Python Layer (Switch Engine)

### Responsibilities

* Transaction lifecycle:

  * 0100 (Authorization)
  * 0200 (Financial)
  * 0400 (Reversal)

* Business rules:

  * Reversal only on timeout
  * No reversal on declines (05/51)

* Security:

  * DUKPT key derivation
  * PIN block generation
  * MAC generation

* State management:

  * STAN allocation
  * RRN generation
  * Transaction status tracking

* Event tracking:

  * Full lifecycle events

* Audit:

  * JSON structured logs
  * JSONL audit trail

* Concurrency:

  * Multi-terminal support
  * Thread-safe operations

---

# 🔄 Transaction Flow

## ✅ Normal Flow

```text
ATM → 0100 → jPOS → Python → DB
                     ↓
                  RC=00
ATM ← 0110 ← jPOS

ATM → 0200 → jPOS → Python → DB
                     ↓
                  RC=00
ATM ← 0210 ← jPOS
```

---

## ⚠️ Timeout → Reversal

```text
0200 → timeout
      ↓
Python triggers 0400
      ↓
Transaction marked REVERSED
```

---

## ❌ Decline Flow

```text
0200 → RC=05
      ↓
NO reversal
      ↓
Status = DECLINED
```

---

# 📊 Transaction State Model

```text
STARTED → AUTHORIZED → COMPLETED

STARTED → DECLINED

STARTED → TIMEOUT → REVERSED
```

---

# 🧾 Event Model

```json
{
  "stan": "123456",
  "rrn": "000000000001",
  "status": "COMPLETED",
  "events": [
    {"event": "transaction.started"},
    {"event": "0100.response"},
    {"event": "0200.response"},
    {"event": "transaction.completed"}
  ]
}
```

---

# 🧱 Production Deployment (Docker)

```text
                ┌───────────────────────────────┐
                │         Docker Host           │
                └─────────────┬─────────────────┘
                              │
      ┌───────────────────────┼────────────────────────┐
      ▼                       ▼                        ▼

┌───────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ jPOS Gateway  │   │ Python Switch    │   │ PostgreSQL DB    │
│ Container     │   │ API Container    │   │ Container         │
│---------------│   │------------------│   │------------------│
│ ISO handling  │   │ Business logic   │   │ transactions      │
│ TCP server    │   │ Reversal engine  │   │ events            │
└──────┬────────┘   └──────┬───────────┘   └──────┬───────────┘
       │ HTTP/gRPC         │ SQL                  │
       ▼                   ▼                      ▼

     Internal Docker Network
```

---

# 🔐 Security Model

* MAC: ANSI X9.19 (K1/K2/K1)
* PIN: ISO-0 PIN block
* DUKPT:

  * BDK + KSN
  * per-transaction keys

---

# 📦 Current Status

| Area           | Status            |
| -------------- | ----------------- |
| ISO8583        | ✅ Complete        |
| MAC            | ✅ Complete        |
| DUKPT          | ✅ Complete        |
| Lifecycle      | ✅ Complete        |
| Reversal Logic | ✅ Complete        |
| Event Tracking | ✅ Complete        |
| Audit Trail    | ✅ Complete        |
| Concurrency    | ✅ Complete        |
| Persistence    | ❌ Not implemented |

---

# ⚠️ Known Gaps

* No database persistence (in-memory only)
* Idempotency not durable
* No reconciliation engine
* No settlement / scheme integration

---

# 🚀 Next Steps

1. Implement persistence layer (DB)
2. Add idempotency (STAN/RRN constraints)
3. Build reconciliation engine
4. Add settlement & TT file generation
5. Convert Python into production service (API)

---

# 🏁 Final Notes

* Java (jPOS) = **Protocol Layer**
* Python = **Switch Core (Business Logic)**
* Database = **Single Source of Truth (next step)**

👉 This is a **modern hybrid switch architecture** used in fintech systems.
