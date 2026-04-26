# ATM Simulator – Risks & Issues Assessment

This document outlines the current risks and technical gaps in the ATM ISO8583 simulator implementation.

---

## 🔴 HIGH RISK (Must Fix)

### 1. MAC Calculation Incorrect
- Current implementation includes field 64 placeholder during MAC calculation.
- Real networks (Visa/Mastercard) will reject this.
- **Fix:** Calculate MAC without field 64.

### 2. No Duplicate Transaction Protection
- Same STAN can be reused.
- Risk: **Double charging transactions**.
- **Fix:** Reject duplicate STAN per terminal.

### 3. Reversal Without Validation
- System sends reversal without verifying original transaction.
- Risk: **Phantom reversals / inconsistent balances**.
- **Fix:** Validate STAN existence and status before reversal.

### 4. No Concurrency Protection
- Multi-threaded writes to transaction_store without locks.
- Risk: **Race conditions / corrupted state**.
- **Fix:** Add threading.Lock()

---

## 🟠 MEDIUM RISK

### 5. Missing RRN (Field 37)
- Only STAN used for tracking.
- Risk: Cannot reconcile across systems.
- **Fix:** Add unique RRN per transaction.

### 6. KSN Counter Not Persisted
- Counter resets every run.
- Risk: **DUKPT key reuse (security issue)**.
- **Fix:** Persist KSN per terminal.

### 7. Over-Aggressive Reversal Logic
- Reversal triggered for all failures.
- Correct behavior:
  - Timeout → YES
  - Decline → NO
- **Fix:** Apply conditional reversal logic.

---

## 🟡 LOW RISK

### 8. No Structured Logging
- Using print statements.
- **Fix:** Implement JSON logging.

### 9. No Retry Strategy
- Immediate reversal on timeout.
- **Fix:** Retry before reversal.

### 10. No Idempotency
- Same request processed multiple times.
- **Fix:** Add request deduplication.

---

## 📊 Current System Status

| Component | Status |
|----------|--------|
| ISO8583 | ✅ Stable |
| DUKPT | ✅ Stable |
| MAC | ⚠️ Needs Fix |
| Lifecycle | ✅ Good |
| STAN Tracking | ✅ Good |
| Concurrency | ❌ Missing |
| Fraud Protection | ❌ Missing |

---

## 🧠 Summary

The system is functionally correct but lacks production-grade safeguards.

Next priorities:
1. Fix MAC calculation
2. Add duplicate detection
3. Add reversal validation
