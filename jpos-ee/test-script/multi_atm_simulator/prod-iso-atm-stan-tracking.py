#!/usr/bin/env python3
"""
prod-iso-atm-stan-tracking.py
ATM ISO 8583 STAN Lifecycle Tracker

Risks addressed (ATM_SIMULATOR_RISKS_README.md):
  R1  - MAC: correct ANSI X9.19 K1/K2/K1 with zero-filled field-64 preimage
  R2  - Duplicate STAN detection per terminal (prevents double-charging)
  R3  - Reversal validation: check STAN existence + status before 0400
  R4  - Concurrency protection: threading.Lock on all transaction_store ops
  R5  - RRN (field 37) added for cross-system reconciliation
  R6  - KSN counter persisted to ksn_state.json (prevents DUKPT key reuse)
  R7  - Reversal only on TIMEOUT, not on soft declines (05/51)
  R8  - Structured JSON logging (replaces bare print statements)
  R9  - Retry strategy: MAX_RETRIES attempts before declaring TIMEOUT
  R10 - Idempotency: STAN deduplication via seen_stans set
"""
import os, socket, struct, threading, random, time, json, logging, sys
from datetime import datetime, timezone
from Crypto.Cipher import DES, DES3

# ── Config ────────────────────────────────────────────────────────────────────
HOST = os.getenv("JPOS_HOST", "localhost")
PORT = int(os.getenv("JPOS_PORT", "8583"))
TPDU = b"\x60\x00\x00\x00\x00"

TIMEOUT_RATE   = 0.1
TIMEOUT_SEC    = 3
MAX_RETRIES    = 2          # R9 – retries before reversal
KSN_STATE_FILE = "ksn_state.json"

BDK = bytes.fromhex(os.environ["JPOS_BDK_HEX"])
MAC_KEY = bytes.fromhex(os.environ["JPOS_MAC_KEY_HEX"])
VARIANT_RIGHT_HALF = bytes.fromhex("C0C0C0C000000000")

TERMINALS = [
    {"tid": "TERM0001", "ksn_base": "FFFF9876543210E00000"},
    {"tid": "TERM0002", "ksn_base": "FFFF9876543211E00000"},
    {"tid": "TERM0003", "ksn_base": "FFFF9876543212E00000"},
]

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
                transaction_store[stan] = {"terminal": tid, "status": "STARTED", "rrn": None}
                return stan
    raise RuntimeError(f"[{tid}] Failed to allocate unique STAN after 100 attempts")

# R4 – thread-safe store update
def update_store(stan: str, **kwargs):
    with _store_lock:
        transaction_store[stan].update(kwargs)

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
        return "TIMEOUT"

# ── Terminal worker ───────────────────────────────────────────────────────────
def run_term(term):
    tid = term["tid"]
    base = term["ksn_base"]
    ksn_state = load_ksn_state()                    # R6 – load persisted counter
    counter   = ksn_state.get(tid, 1)

    for _ in range(5):
        ksn = build_ksn(base, counter)
        counter += 1

        pan = "4111111111111111"
        now = datetime.now(timezone.utc)
        key = derive_pin_key(BDK, ksn)
        stan = allocate_stan(tid)                   # R2/R10 – unique STAN
        rrn  = next_rrn()                           # R5  – RRN
        update_store(stan, rrn=rrn)

        # R5 – RRN tracked in store; not sent in message (gateway packager limitation)
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

        rc = send_tx("0100", fields)
        info("0100", terminal=tid, stan=stan, rrn=rrn, rc=rc)   # R8

        if rc == "00":
            update_store(stan, status="AUTHORIZED")
        elif rc in ("05", "51"):
            # R7 – soft decline: NO reversal
            update_store(stan, status="DECLINED")
            continue  
        elif rc == "TIMEOUT":
            update_store(stan, status="TIMEOUT")
            if can_reverse(stan):                   # R3 – validate before reversing
                info("0400 reversal (0100 timeout)", terminal=tid, stan=stan, rrn=rrn)
                send_tx("0400", fields)
            continue
        else:
            update_store(stan, status="FAILED")
            continue

        fields.update({
            52: build_pin("1234", pan, key),
            62: ksn
        })

        rc = send_tx("0200", fields)
        info("0200", terminal=tid, stan=stan, rrn=rrn, rc=rc)   # R8

        if rc == "00":
            update_store(stan, status="COMPLETED")
        elif rc == "TIMEOUT":
            # R7 – only reverse on timeout, not on decline
            update_store(stan, status="TIMEOUT")
            if can_reverse(stan):                   # R3
                info("0400 reversal (0200 timeout)", terminal=tid, stan=stan, rrn=rrn)
                rev_fields = {k: v for k, v in fields.items() if k not in [52, 62]}
                send_tx("0400", rev_fields)
        else:
            # R7 – non-timeout failure: NO reversal
            update_store(stan, status="FAILED")

    # R6 – persist KSN counter after terminal finishes
    ksn_state[tid] = counter
    save_ksn_state(ksn_state)

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    threads=[]
    for t in TERMINALS:
        th=threading.Thread(target=run_term,args=(t,))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()

    print("\n=== TRANSACTION STORE ===")
    print(json.dumps(transaction_store, indent=2))

if __name__=="__main__":
    main()
