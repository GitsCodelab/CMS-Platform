# Multi ATM Simulator (Production Logic)

This simulator runs multiple ATM terminals in parallel against the jPOS gateway using full ISO 8583 + DUKPT + MAC logic.

## End-to-End Flow

Multiple ATMs (Python workers)  
-> ISO8583 + DUKPT + MAC  
-> Gateway (Java jPOS)  
-> Validation + Routing  
-> Response

## What This Test Covers

1. Parallel terminal traffic using worker threads (`TERM0001`, `TERM0002`, `TERM0003`).
2. Per-transaction KSN progression per terminal (`terminal_state.json`).
3. DUKPT PIN key derivation and encrypted field 52 PIN block.
4. ANSI X9.19 MAC generation for field 64.
5. ISO 8583 packing and unpacking against jPOS parser.
6. Correct response-code extraction from field 39 (not from last raw byte).

## Crypto + Message Logic (Current)

1. DUKPT:
- `derive_pin_key()` derives a per-transaction key from `JPOS_BDK_HEX` + terminal KSN.
- `build_pin()` creates ISO-0 clear PIN block and encrypts it with 3DES.

2. MAC (field 64):
- `mac_x919()` uses ANSI X9.19 2-key finalization (`K1/K2/K1`).
- MAC is calculated over the packed message with field 64 set to 8 zero bytes placeholder.

3. ISO Packing:
- Numeric fields are right-nibble padded BCD when odd length.
- Field 52 is sent as raw 8-byte binary.
- Field 62 carries KSN as ASCII LLLVAR.

4. Response Parsing:
- `get_response_code()` parses bitmap and walks fields to extract field 39 exactly.

## Prerequisites

1. jPOS gateway is running and healthy on `localhost:8583`.
2. `.env` is loaded in this folder.
3. Python virtual environment has crypto dependency installed (`pycryptodome`).

## Run

```bash
cd /home/samehabib/CMS-Platform/jpos-ee/test-script/multi_atm_simulator
set -a && source .env && set +a
python3 prod-iso-atm-test.py --with-mac
```

## Expected Output

All workers should print successful response codes:

```text
[TERM0001] RC=00
[TERM0002] RC=00
[TERM0003] RC=00
...
```

## Troubleshooting

1. `RC=96` (System/MAC validation failure):
- Verify `JPOS_MAC_KEY_HEX` matches gateway runtime key.
- Ensure MAC is calculated with field 64 zero placeholder before final insertion.

2. `RC=55` (DUKPT/PIN failure):
- Check BDK and KSN progression logic.
- Ensure field 52 remains binary 8 bytes.

3. `ConnectionRefusedError`:
- Start gateway and wait until healthy.

4. Wrong RC values like random hex (`7E`, `69`, ...):
- This indicates parsing the wrong byte; use field-39 parser (`get_response_code`).

## Files

- `prod-iso-atm-test.py`: Multi-terminal simulator with DUKPT + MAC + ISO parsing.
- `.env`: Test runtime host/port and key material.
- `terminal_state.json`: Runtime terminal counter state (KSN progression).
