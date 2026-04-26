# Multi ATM Simulator (End-to-End)

This folder is now organized around one primary simulator:

- `atm_iso8583_end_to_end_simulator.py`

Legacy variants were removed so all testing uses one maintained script and one consistent behavior model.

## What This Simulator Covers

1. Full ISO 8583 transaction lifecycle: `0100 -> 0200 -> optional 0400`.
2. DUKPT PIN encryption with per-transaction KSN.
3. ANSI X9.19 MAC generation (K1/K2/K1) with zero-filled field-64 preimage.
4. Thread-safe STAN allocation and transaction state updates.
5. Deterministic fault injection for end-to-end scenario tests.
6. Event-level tracking and JSONL audit trail for reconciliation.

## Prerequisites

1. jPOS gateway running on configured host/port.
2. `.env` loaded in this folder.
3. Python dependency installed: `pycryptodome`.

## Setup

```bash
cd /home/samehabib/CMS-Platform/jpos-ee/test-script/multi_atm_simulator
python3 -m pip install pycryptodome
set -a && source .env && set +a
```

## Commands

### 1) Syntax check

```bash
python3 -m py_compile atm_iso8583_end_to_end_simulator.py
```

### 2) Live End-to-End run

```bash
python3 atm_iso8583_end_to_end_simulator.py
```

### 3) Deterministic scenario tests

Timeout on 0200, reversal succeeds:

```bash
ATM_TERMINAL_COUNT=1 ATM_TX_PER_TERMINAL=1 \
TEST_RC_PLAN='{"0100":["00"],"0200":["TIMEOUT"],"0400":["00"]}' \
python3 atm_iso8583_end_to_end_simulator.py
```

Decline on 0200, no reversal:

```bash
ATM_TERMINAL_COUNT=1 ATM_TX_PER_TERMINAL=1 \
TEST_RC_PLAN='{"0100":["00"],"0200":["05"]}' \
python3 atm_iso8583_end_to_end_simulator.py
```

Timeout on 0100, reversal timeout:

```bash
ATM_TERMINAL_COUNT=1 ATM_TX_PER_TERMINAL=1 \
TEST_RC_PLAN='{"0100":["TIMEOUT"],"0400":["TIMEOUT"]}' \
python3 atm_iso8583_end_to_end_simulator.py
```

### 4) Field 37 reconciliation capability

```bash
ATM_TERMINAL_COUNT=1 ATM_TX_PER_TERMINAL=1 ATM_SEND_RRN_FIELD37=1 \
TEST_RC_PLAN='{"0100":["00"],"0200":["00"]}' \
python3 atm_iso8583_end_to_end_simulator.py
```

### 5) Audit trail output

```bash
rm -f atm_audit_trail.jsonl
ATM_TERMINAL_COUNT=1 ATM_TX_PER_TERMINAL=1 ATM_WRITE_AUDIT_LOG=1 \
TEST_RC_PLAN='{"0100":["00"],"0200":["TIMEOUT"],"0400":["00"]}' \
python3 atm_iso8583_end_to_end_simulator.py
wc -l atm_audit_trail.jsonl
```

## Expected Results

1. Normal flow: `COMPLETED`.
2. Timeout + successful reversal: `REVERSED`.
3. Timeout + reversal timeout: `REVERSAL_TIMEOUT`.
4. Decline `05/51`: `DECLINED` with no reversal event.
