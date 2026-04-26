#!/usr/bin/env python3
"""
atm_iso8583_end_to_end_simulator.py
ATM ISO 8583 STAN Lifecycle Tracker

Risks addressed (ATM_SIMULATOR_RISKS_README.md):
  R1  - MAC: correct ANSI X9.19 K1/K2/K1 with zero-filled field-64 preimage
  R2  - Duplicate STAN detection per terminal (prevents double-charging)
  R3  - Reversal validation: check STAN existence + status before 0400
  R4  - Concurrency protection: threading.Lock on all transaction_store ops
    R5  - RRN generated and tracked in store for cross-system reconciliation
  R6  - KSN counter persisted to ksn_state.json (prevents DUKPT key reuse)
  R7  - Reversal only on TIMEOUT, not on soft declines (05/51)
  R8  - Structured JSON logging (replaces bare print statements)
  R9  - Retry strategy: MAX_RETRIES attempts before declaring TIMEOUT
  R10 - Idempotency: STAN deduplication via seen_stans set
"""
import os, socket, struct, threading, random, time, json, logging, sys
from datetime import datetime, timezone
from Crypto.Cipher import DES, DES3


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

# ── Config ────────────────────────────────────────────────────────────────────
HOST = os.getenv("JPOS_HOST", "localhost")
PORT = int(os.getenv("JPOS_PORT", "8583"))
TPDU = b"\x60\x00\x00\x00\x00"

TIMEOUT_RATE   = float(os.getenv("JPOS_TIMEOUT_RATE", "0.1"))
TIMEOUT_SEC    = int(os.getenv("JPOS_TIMEOUT_SEC", "3"))
MAX_RETRIES    = int(os.getenv("JPOS_MAX_RETRIES", "2"))   # R9 – retries before reversal
KSN_STATE_FILE = "ksn_state.json"
TX_PER_TERMINAL = int(os.getenv("ATM_TX_PER_TERMINAL", "5"))
TERMINAL_COUNT  = int(os.getenv("ATM_TERMINAL_COUNT", "3"))
SEND_RRN_FIELD37 = os.getenv("ATM_SEND_RRN_FIELD37", "0") == "1"
AUDIT_LOG_FILE = os.getenv("ATM_AUDIT_LOG_FILE", "atm_audit_trail.jsonl")
WRITE_AUDIT_LOG = os.getenv("ATM_WRITE_AUDIT_LOG", "1") == "1"

BDK = bytes.fromhex(os.environ["JPOS_BDK_HEX"])
MAC_KEY = bytes.fromhex(os.environ["JPOS_MAC_KEY_HEX"])
VARIANT_RIGHT_HALF = bytes.fromhex("C0C0C0C000000000")

TERMINALS_ALL = [
    {"tid": "TERM0001", "ksn_base": "FFFF9876543210E00000"},
    {"tid": "TERM0002", "ksn_base": "FFFF9876543211E00000"},
    {"tid": "TERM0003", "ksn_base": "FFFF9876543212E00000"},
]
TERMINALS = TERMINALS_ALL[:max(1, min(TERMINAL_COUNT, len(TERMINALS_ALL)))]

# End-to-end deterministic test plan. Example:
# TEST_RC_PLAN='{"0100":["00","TIMEOUT"],"0200":["05"],"0400":["00"]}'
_test_plan_lock = threading.Lock()
try:
    _test_rc_plan = json.loads(os.getenv("TEST_RC_PLAN", "{}"))
except json.JSONDecodeError:
    _test_rc_plan = {}

# Built-in deterministic EndToEnd test catalog.
TEST_CASES = [
    {
        "id": "TC01",
        "name": "0200 timeout then successful reversal",
        "description": "Authorization succeeds, financial message times out, and 0400 completes successfully.",
        "plan": {"0100": ["00"], "0200": ["TIMEOUT"], "0400": ["00"]},
        "expected_status": "REVERSED",
        "expected_reversal": "executed"
    },
    {
        "id": "TC02",
        "name": "0200 decline without reversal",
        "description": "Authorization succeeds, financial message is declined (05/51), and no 0400 is sent.",
        "plan": {"0100": ["00"], "0200": ["05"]},
        "expected_status": "DECLINED",
        "expected_reversal": "not_sent"
    },
    {
        "id": "TC03",
        "name": "0100 timeout then successful reversal",
        "description": "Authorization request times out and triggers 0400 which succeeds.",
        "plan": {"0100": ["TIMEOUT"], "0400": ["00"]},
        "expected_status": "REVERSED",
        "expected_reversal": "executed"
    },
    {
        "id": "TC04",
        "name": "0100 hard failure without reversal",
        "description": "Authorization fails with non-timeout RC (e.g. 96), and no reversal is sent.",
        "plan": {"0100": ["96"]},
        "expected_status": "FAILED",
        "expected_reversal": "not_sent"
    },
    {
        "id": "TC05",
        "name": "Reversal timeout",
        "description": "Authorization times out, 0400 is sent, and reversal itself times out.",
        "plan": {"0100": ["TIMEOUT"], "0400": ["TIMEOUT"]},
        "expected_status": "REVERSAL_TIMEOUT",
        "expected_reversal": "timeout"
    },
    {
        "id": "TC06",
        "name": "Field 37 capability",
        "description": "RRN can be injected into ISO messages when ATM_SEND_RRN_FIELD37=1 for reconciliation-enabled profiles.",
        "plan": {"0100": ["00"], "0200": ["00"]},
        "expected_status": "COMPLETED",
        "expected_reversal": "not_sent"
    }
]


def print_test_catalog():
    info("EndToEnd test catalog", cases=TEST_CASES)

def _planned_rc(mti: str):
    with _test_plan_lock:
        plan = _test_rc_plan.get(mti)
        if plan is None:
            return None
        if isinstance(plan, str):
            return plan
        if isinstance(plan, list) and plan:
            return plan.pop(0)
        return None

# ── R8 – Structured JSON logging ──────────────────────────────────────────────
class _JsonFormatter(logging.Formatter):
    def format(self, record):
        entry = {
            "ts":    datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "msg":   record.getMessage(),
        }
        if hasattr(record, "_extra"):
            entry.update(record._extra)
        return json.dumps(entry)

_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(_JsonFormatter())
_log = logging.getLogger("atm")
_log.setLevel(logging.INFO)
_log.addHandler(_handler)

def _logx(level, msg, **kw):
    r = _log.makeRecord(_log.name, level, "", 0, msg, [], None)
    r._extra = kw
    _log.handle(r)

def info(msg, **kw):  _logx(logging.INFO,    msg, **kw)
def warn(msg, **kw):  _logx(logging.WARNING, msg, **kw)
def err(msg,  **kw):  _logx(logging.ERROR,   msg, **kw)

# ── R4 – Concurrency protection ───────────────────────────────────────────────
_store_lock = threading.Lock()
transaction_store: dict = {}
_audit_lock = threading.Lock()


def _append_audit(entry: dict):
    if not WRITE_AUDIT_LOG:
        return
    with _audit_lock:
        with open(AUDIT_LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")

# R10 – idempotency / R2 – duplicate STAN
_seen_stans: set = set()

# ── R6 – Persisted KSN state ──────────────────────────────────────────────────
_ksn_lock = threading.Lock()

def load_ksn_state() -> dict:
    try:
        with open(KSN_STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {t["tid"]: 1 for t in TERMINALS}

def save_ksn_state(state: dict):
    with _ksn_lock:
        with open(KSN_STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)

# ── Crypto helpers ────────────────────────────────────────────────────────────
def xor(a,b): return bytes(x^y for x,y in zip(a,b))
def des_enc(k,d): return DES.new(k, DES.MODE_ECB).encrypt(d)
def des_dec(k,d): return DES.new(k, DES.MODE_ECB).decrypt(d)

def tdes_enc(k,d): return DES3.new(k[:16]+k[:8], DES3.MODE_ECB).encrypt(d)

def shift_right(v):
    carry=0
    for i in range(len(v)):
        new=v[i]&1
        v[i]=((v[i]>>1)|(carry<<7))&0xFF
        carry=new

def derive_pin_key(bdk, ksn_hex):
    ksn = bytes.fromhex(ksn_hex)
    padded = ksn.hex().upper().rjust(20, "F")
    iksn = bytearray(bytes.fromhex(padded[:16]))
    iksn[7] &= 0xE0
    lb, rb = bdk[:8], bdk[8:16]
    def ede(k, d):
        return des_enc(k[:8], des_dec(k[8:16], des_enc(k[:8], d)))
    cur = bytearray(
        ede(bdk[:16], bytes(iksn)) +
        ede(xor(lb, VARIANT_RIGHT_HALF)+xor(rb, VARIANT_RIGHT_HALF), bytes(iksn))
    )
    ksn_b = bytearray(bytes.fromhex(ksn.hex()[-16:]))
    ksn_b[4] &= 0xE0
    tc = bytearray(ksn[-3:])
    tc[0] &= 0x1F
    sr = bytearray(bytes.fromhex("100000"))
    while any(sr):
        if any((sr[i]&tc[i])!=0 for i in range(3)):
            l, r = bytes(cur[:8]), bytes(cur[8:16])
            for i in range(3): ksn_b[5+i] |= sr[i]
            cr1 = xor(des_enc(l, xor(bytes(ksn_b), r)), r)
            lv, rv = xor(l, VARIANT_RIGHT_HALF), xor(r, VARIANT_RIGHT_HALF)
            cr2 = xor(des_enc(lv, xor(bytes(ksn_b), rv)), rv)
            cur = bytearray(cr2 + cr1)
        shift_right(sr)
    cur[7] ^= 0xFF
    cur[15] ^= 0xFF
    return bytes(cur)

def build_pin(pin, pan, key):
    pb = bytes.fromhex(f"0{len(pin)}{pin}" + "F"*(16-len(pin)-2))
    panb = bytes.fromhex("0000"+pan[-13:-1])
    return tdes_enc(key, xor(pb, panb))

def build_ksn(base, counter):
    b = bytearray(bytes.fromhex(base))
    b[-3:] = counter.to_bytes(3, "big")
    return b.hex().upper()

# R1 – ANSI X9.19 MAC: K1/K2/K1 with zero-filled field-64 preimage
def mac_x919(key, data):
    k1, k2 = key[:8], key[8:16]
    padded = data + (b"\x00" * ((8 - len(data) % 8) % 8))
    state = b"\x00" * 8
    for i in range(0, len(padded), 8):
        state = des_enc(k1, xor(state, padded[i:i+8]))
    state = DES.new(k2, DES.MODE_ECB).decrypt(state)
    state = DES.new(k1, DES.MODE_ECB).encrypt(state)
    return state

# ── ISO 8583 packing ──────────────────────────────────────────────────────────
def pack_msg(mti, fields, macv=None):
    fset = set(fields)
    if macv: fset.add(64)

    bmp = 0
    for f in fset:
        bmp |= (1 << (64-f))

    data = bytes.fromhex(mti) + bmp.to_bytes(8, "big")

    for f in sorted(fset):
        if f == 64:
            data += macv
            continue
        v = fields[f]
        if f == 2:
            l = f"{len(v):02}"
            data += bytes.fromhex(l) + bytes.fromhex(v if len(v)%2==0 else v+"0")
        elif f == 37:                                # R5 – RRN: 12-char ASCII
            data += str(v).ljust(12).encode()[:12]
        elif f in [3,4,7,11,12,13,22,25,49]:
            lens = {3:6, 4:12, 7:10, 11:6, 12:6, 13:4, 22:3, 25:2, 49:3}
            val = v.zfill(lens[f])
            if len(val) % 2: val += "0"
            data += bytes.fromhex(val)
        elif f in [41, 42]:
            lens = {41:8, 42:15}
            data += v.encode().ljust(lens[f], b" ")
        elif f == 52:
            data += v
        elif f == 62:
            data += f"{len(v):03}".encode() + v.encode()

    return data

# ── Response parser ───────────────────────────────────────────────────────────
def get_rc(resp):
    if resp is None:
        return "TIMEOUT"
    payload = resp[2:]
    iso     = payload[5:]
    bitmap  = int.from_bytes(iso[2:10], "big")
    fields  = [f for f in range(1, 65) if bitmap & (1 << (64-f))]
    offset  = 10
    for f in fields:
        if f == 39:
            b = iso[offset]
            return f"{(b>>4)&0xF}{b&0xF}"
        elif f == 2:
            l = (iso[offset]>>4)*10 + (iso[offset]&0xF)
            offset += 1 + (l+1)//2
        elif f == 3:   offset += 3
        elif f == 4:   offset += 6
        elif f == 7:   offset += 5
        elif f == 11:  offset += 3
        elif f == 12:  offset += 3
        elif f == 13:  offset += 2
        elif f == 22:  offset += 2
        elif f == 25:  offset += 1
        elif f == 37:  offset += 12   # R5 – RRN
        elif f == 38:  offset += 6    # auth code (before field 39)
        elif f == 41:  offset += 8
        elif f == 42:  offset += 15
        elif f == 49:  offset += 2
        elif f == 52:  offset += 8
        elif f == 62:
            l = int(iso[offset:offset+3].decode())
            offset += 3 + l
        elif f == 64:  offset += 8
    return "??"

# ── Network ───────────────────────────────────────────────────────────────────
def _send_raw(msg):
    if random.random() < TIMEOUT_RATE:
        warn("Network timeout simulated")
        time.sleep(TIMEOUT_SEC)
        return None
    with socket.socket() as s:
        s.settimeout(TIMEOUT_SEC)
        s.connect((HOST, PORT))
        s.sendall(msg)
        return s.recv(4096)

# R9 – Retry strategy: up to MAX_RETRIES before declaring TIMEOUT
def _send_with_retry(msg):
    for attempt in range(1, MAX_RETRIES + 2):
        resp = _send_raw(msg)
        if resp is not None:
            return resp
        if attempt <= MAX_RETRIES:
            warn(f"Retry {attempt}/{MAX_RETRIES} after timeout")
    return None

def send_tx(mti, fields):
    injected = _planned_rc(mti)
    if injected is not None:
        warn("Test RC injected", mti=mti, injected_rc=injected)
        return injected

    # R1 – pack with zero field-64, compute MAC, re-pack with real MAC
    temp = pack_msg(mti, fields, macv=b"\x00"*8)
    mac  = mac_x919(MAC_KEY, temp)
    body = pack_msg(mti, fields, mac)
    msg  = struct.pack(">H", len(TPDU+body)) + TPDU + body
    return get_rc(_send_with_retry(msg))

# ── R5 – RRN generator ────────────────────────────────────────────────────────
_rrn_lock    = threading.Lock()
_rrn_counter = 0

def next_rrn() -> str:
    global _rrn_counter
    with _rrn_lock:
        _rrn_counter += 1
        return str(_rrn_counter).zfill(12)

# ── R2 / R10 – STAN allocation (duplicate-safe, idempotent) ──────────────────
def allocate_stan(tid: str) -> str:
    with _store_lock:
        for _ in range(100):
            stan = str(random.randint(0, 999999)).zfill(6)
            if stan not in _seen_stans:
                _seen_stans.add(stan)
                transaction_store[stan] = {
                    "terminal": tid,
                    "status": "STARTED",
                    "rrn": None,
                    "created_at": _utc_now(),
                    "events": []
                }
                return stan
    raise RuntimeError(f"[{tid}] Failed to allocate unique STAN after 100 attempts")

# R4 – thread-safe store update
def update_store(stan: str, **kwargs):
    with _store_lock:
        transaction_store[stan].update(kwargs)


def add_event(stan: str, event_type: str, **details):
    event = {"ts": _utc_now(), "event": event_type, **details}
    with _store_lock:
        if stan in transaction_store:
            transaction_store[stan].setdefault("events", []).append(event)
            entry = {
                "stan": stan,
                "terminal": transaction_store[stan].get("terminal"),
                "rrn": transaction_store[stan].get("rrn"),
                **event
            }
        else:
            entry = {"stan": stan, **event}
    _append_audit(entry)

# ── R3 – Reversal validation ──────────────────────────────────────────────────
def can_reverse(stan: str) -> bool:
    with _store_lock:
        entry = transaction_store.get(stan)
        if entry is None:
            err("Reversal rejected: STAN not in store", stan=stan)
            return False
        if entry["status"] not in ("AUTHORIZED", "TIMEOUT", "STARTED"):
            warn("Reversal skipped: not in reversible state", stan=stan, status=entry["status"])
            return False
        return True

def do_reversal(tid: str, stan: str, rrn: str, rev_fields: dict, reason: str):
    add_event(stan, "0400.requested", mti="0400", reason=reason)
    info("0400 reversal requested", terminal=tid, stan=stan, rrn=rrn, reason=reason)
    rc = send_tx("0400", rev_fields)
    add_event(stan, "0400.response", mti="0400", rc=rc)
    info("0400 reversal response", terminal=tid, stan=stan, rrn=rrn, rc=rc)
    if rc == "00":
        update_store(stan, status="REVERSED", reversal_rc=rc)
    elif rc == "TIMEOUT":
        # Explicitly track uncertain reversal outcome for operator follow-up.
        update_store(stan, status="REVERSAL_TIMEOUT", reversal_rc=rc)
    else:
        update_store(stan, status="REVERSAL_FAILED", reversal_rc=rc)

# ── Terminal worker ───────────────────────────────────────────────────────────
def run_term(term):
    tid = term["tid"]
    base = term["ksn_base"]
    ksn_state = load_ksn_state()                    # R6 – load persisted counter
    counter   = ksn_state.get(tid, 1)

    for _ in range(TX_PER_TERMINAL):
        ksn = build_ksn(base, counter)
        counter += 1

        pan = "4111111111111111"
        now = datetime.now(timezone.utc)
        key = derive_pin_key(BDK, ksn)
        stan = allocate_stan(tid)                   # R2/R10 – unique STAN
        rrn  = next_rrn()                           # R5  – RRN
        update_store(stan, rrn=rrn)
        add_event(stan, "transaction.started", mti="0000", status="STARTED")

        # R5 – RRN is always tracked in store. Field 37 is optional by profile.
        fields = {
            2: pan,
            3:"000000",
            4:"000000010000",
            7: now.strftime("%m%d%H%M%S"),
            11: stan,
            12: now.strftime("%H%M%S"),
            13: now.strftime("%m%d"),
            22:"051",
            25:"00",
            41: tid,
            42:"MERCHANT000001",
            49:"840"
        }
        if SEND_RRN_FIELD37:
            fields[37] = rrn

        rc = send_tx("0100", fields)
        add_event(stan, "0100.response", mti="0100", rc=rc, rrn_field37_sent=SEND_RRN_FIELD37)
        info("0100", terminal=tid, stan=stan, rrn=rrn, rc=rc)   # R8

        if rc == "00":
            update_store(stan, status="AUTHORIZED")
        elif rc in ("05", "51"):
            # R7 – soft decline: NO reversal
            update_store(stan, status="DECLINED", auth_rc=rc)
            add_event(stan, "transaction.declined", mti="0100", rc=rc)
            continue  
        elif rc == "TIMEOUT":
            update_store(stan, status="TIMEOUT")
            add_event(stan, "transaction.timeout", mti="0100", rc=rc)
            if can_reverse(stan):                   # R3 – validate before reversing
                do_reversal(tid, stan, rrn, fields, reason="0100 timeout")
            continue
        else:
            update_store(stan, status="FAILED", auth_rc=rc)
            add_event(stan, "transaction.failed", mti="0100", rc=rc)
            continue

        fields.update({
            52: build_pin("1234", pan, key),
            62: ksn
        })

        rc = send_tx("0200", fields)
        add_event(stan, "0200.response", mti="0200", rc=rc, rrn_field37_sent=SEND_RRN_FIELD37)
        info("0200", terminal=tid, stan=stan, rrn=rrn, rc=rc)   # R8

        if rc == "00":
            update_store(stan, status="COMPLETED")
            add_event(stan, "transaction.completed", mti="0200", rc=rc)
        elif rc == "TIMEOUT":
            # R7 – only reverse on timeout, not on decline
            update_store(stan, status="TIMEOUT")
            add_event(stan, "transaction.timeout", mti="0200", rc=rc)
            if can_reverse(stan):                   # R3
                rev_fields = {k: v for k, v in fields.items() if k not in [52, 62]}
                do_reversal(tid, stan, rrn, rev_fields, reason="0200 timeout")
        elif rc in ("05", "51"):
            # R7 – soft decline: NO reversal
            update_store(stan, status="DECLINED", financial_rc=rc)
            add_event(stan, "transaction.declined", mti="0200", rc=rc)
        else:
            # R7 – non-timeout failure: NO reversal
            update_store(stan, status="FAILED", financial_rc=rc)
            add_event(stan, "transaction.failed", mti="0200", rc=rc)

    # R6 – persist KSN counter after terminal finishes
    ksn_state[tid] = counter
    save_ksn_state(ksn_state)

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print_test_catalog()

    threads=[]
    for t in TERMINALS:
        th=threading.Thread(target=run_term,args=(t,))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()

    counts = {}
    for tx in transaction_store.values():
        s = tx.get("status", "UNKNOWN")
        counts[s] = counts.get(s, 0) + 1

    print("\n=== TRANSACTION STORE ===")
    print(json.dumps(transaction_store, indent=2))
    print("\n=== STATUS SUMMARY ===")
    print(json.dumps(counts, indent=2))

if __name__=="__main__":
    main()
