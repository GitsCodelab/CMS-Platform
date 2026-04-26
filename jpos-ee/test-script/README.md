# jPOS ISO8583 Test Script (Organized)

This folder is organized around one primary test runner:

- `multi_atm_simulator/atm_iso8583_end_to_end_simulator.py`

All legacy one-off scripts were removed to reduce duplication and keep one reliable source of truth for testing.

## Folder Layout (Active)

- `README.md` - This runbook.
- `README-TEST-RESULT.md` - Historical test findings and fixes.
- `multi_atm_simulator/.env` - Runtime configuration (host, port, keys).
- `multi_atm_simulator/atm_iso8583_end_to_end_simulator.py` - Main End-to-End simulator.
- `multi_atm_simulator/README.md` - Simulator-specific usage details.
- `multi_atm_simulator/ATM_SIMULATOR_RISKS_README.md` - Risk list reference.
- `multi_atm_simulator/risk2.md` - Post-fix validation verdict.
- `multi_atm_simulator/ksn_state.json` - Persisted DUKPT counters.

## Prerequisites

1. Python 3.10+.
2. `pycryptodome` installed.
3. jPOS gateway reachable on configured host/port.
4. Environment variables loaded from `.env`.

## Setup

```bash
cd /home/samehabib/CMS-Platform/jpos-ee/test-script/multi_atm_simulator
python3 -m pip install pycryptodome
set -a && source .env && set +a
```

## Test Commands

### 1) Syntax Validation

```bash
cd /home/samehabib/CMS-Platform/jpos-ee/test-script/multi_atm_simulator
python3 -m py_compile atm_iso8583_end_to_end_simulator.py
```

### 2) Live End-to-End Run (Gateway integration)

```bash
cd /home/samehabib/CMS-Platform/jpos-ee/test-script/multi_atm_simulator
set -a && source .env && set +a
python3 atm_iso8583_end_to_end_simulator.py
```

### 3) Deterministic Single-Case Runs

Run one terminal and one transaction with injected RC plans.

- Timeout on 0200 then reversal success:
```bash
cd /home/samehabib/CMS-Platform/jpos-ee/test-script/multi_atm_simulator
set -a && source .env && set +a
ATM_TERMINAL_COUNT=1 ATM_TX_PER_TERMINAL=1 \
TEST_RC_PLAN='{"0100":["00"],"0200":["TIMEOUT"],"0400":["00"]}' \
python3 atm_iso8583_end_to_end_simulator.py
```

- Decline on 0200 (no reversal):
```bash
cd /home/samehabib/CMS-Platform/jpos-ee/test-script/multi_atm_simulator
set -a && source .env && set +a
ATM_TERMINAL_COUNT=1 ATM_TX_PER_TERMINAL=1 \
TEST_RC_PLAN='{"0100":["00"],"0200":["05"]}' \
python3 atm_iso8583_end_to_end_simulator.py
```

- Timeout on 0100 then reversal timeout:
```bash
cd /home/samehabib/CMS-Platform/jpos-ee/test-script/multi_atm_simulator
set -a && source .env && set +a
ATM_TERMINAL_COUNT=1 ATM_TX_PER_TERMINAL=1 \
TEST_RC_PLAN='{"0100":["TIMEOUT"],"0400":["TIMEOUT"]}' \
python3 atm_iso8583_end_to_end_simulator.py
```

### 4) Reconciliation Capability (Field 37 enabled)

```bash
cd /home/samehabib/CMS-Platform/jpos-ee/test-script/multi_atm_simulator
set -a && source .env && set +a
ATM_TERMINAL_COUNT=1 ATM_TX_PER_TERMINAL=1 ATM_SEND_RRN_FIELD37=1 \
TEST_RC_PLAN='{"0100":["00"],"0200":["00"]}' \
python3 atm_iso8583_end_to_end_simulator.py
```

### 5) Audit Trail Verification

```bash
cd /home/samehabib/CMS-Platform/jpos-ee/test-script/multi_atm_simulator
rm -f atm_audit_trail.jsonl
set -a && source .env && set +a
ATM_TERMINAL_COUNT=1 ATM_TX_PER_TERMINAL=1 ATM_WRITE_AUDIT_LOG=1 \
TEST_RC_PLAN='{"0100":["00"],"0200":["TIMEOUT"],"0400":["00"]}' \
python3 atm_iso8583_end_to_end_simulator.py
wc -l atm_audit_trail.jsonl
head -n 5 atm_audit_trail.jsonl
```

## Expected Outcomes

- Successful transactions end with `COMPLETED`.
- Timeout + successful reversal ends with `REVERSED`.
- Timeout + reversal timeout ends with `REVERSAL_TIMEOUT`.
- Declines (`05`, `51`) end with `DECLINED` and no `0400` event.
- Audit file contains one JSON object per event.
