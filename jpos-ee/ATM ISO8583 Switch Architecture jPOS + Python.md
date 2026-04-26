# 🏗️ ATM ISO8583 Switch Architecture (jPOS + Python)

## 🎯 Overview

This system implements a **hybrid ATM switch architecture** combining:

* **Java (jPOS EE)** → ISO8583 gateway & protocol layer
* **Python** → transaction lifecycle & business logic (switch engine)

---

## 🧠 Architecture Summary

```
ATM / Simulator
      ↓
Java Gateway (jPOS)
      ↓
Python Switch Engine
      ↓
Database (Persistence - upcoming)
      ↓
Core Banking / External Systems
```

---

## 🧩 Components Breakdown

### 🟡 Java Layer (jPOS EE)

#### 1. Gateway (`Gateway.java`)

* TCP socket server
* Handles client connections
* Reads/writes ISO messages
* Delegates processing to ISO handler

#### 2. ISO Handler (`ISOMessageHandler.java`)

* ISO8583 parsing & validation
* Field validation (PAN, STAN, etc.)
* MAC validation (ANSI X9.19)
* DUKPT validation
* Replay protection
* Builds ISO responses

#### 3. Configuration (`AppConfig.java`)

* Loads environment variables
* Manages:

  * MAC keys
  * BDK keys
  * timeouts
  * security flags

#### 4. Packager (`iso87.xml`)

* Defines ISO8583 message structure
* Field formats, lengths, encoding

---

### 🟢 Python Layer (Switch Engine)

Main file: `atm_iso8583_end_to_end_simulator.py`

#### Responsibilities

* Transaction lifecycle management:

  * 0100 (Authorization)
  * 0200 (Financial)
  * 0400 (Reversal)

* Business rules:

  * Reversal on timeout only
  * No reversal on declines (05/51)
  * Retry logic before timeout

* Security:

  * DUKPT key derivation
  * PIN block generation
  * MAC generation (ANSI X9.19)

* State management:

  * STAN allocation (unique)
  * RRN generation
  * Transaction status tracking

* Event tracking:

  * Full lifecycle logging per transaction
  * MTI-based event history

* Audit:

  * Structured JSON logging
  * JSONL audit trail file

* Concurrency:

  * Multi-terminal simulation
  * Thread-safe state updates

---

## 🔁 Transaction Flow

```
ATM → 0100 → Java → Python
                 ↓
           Process logic
                 ↓
           Return RC (00/05/etc)
                 ↓
ATM ← 0110 ← Java

ATM → 0200 → Java → Python
                 ↓
           Process logic
                 ↓
           Return RC
                 ↓
ATM ← 0210 ← Java

If timeout:
Python triggers 0400 (Reversal)
```

---

## 🔐 Security Model

* MAC: ANSI X9.19 (K1/K2/K1)
* PIN: ISO-0 PIN block
* Key Management:

  * BDK (Base Derivation Key)
  * KSN (Key Serial Number)
* DUKPT:

  * Per-transaction key derivation
  * KSN counter persistence

---

## 📊 Transaction State Model

```
STARTED
  ↓
AUTHORIZED
  ↓
COMPLETED

OR

STARTED → DECLINED

OR

STARTED → TIMEOUT → REVERSED
```

---

## 🧾 Event Model

Each transaction contains:

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

## 📦 Current State

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

## ⚠️ Known Gaps

* No database persistence (in-memory only)
* Idempotency not durable across restarts
* No reconciliation engine yet
* No settlement / scheme integration yet

---

## 🚀 Next Steps

1. Add persistence layer (DB)
2. Implement idempotency using DB constraints
3. Build reconciliation engine
4. Add settlement & TT file generation
5. Integrate Python as production service (API)

---

## 🏁 Final Notes

* Java (jPOS) = **Protocol Layer**
* Python = **Switch Core (Business Logic)**
* Database = **Single Source of Truth (upcoming)**

👉 This architecture follows a **hybrid modern switch design** used in fintech systems.
