#!/usr/bin/env python3
import os, socket, struct, argparse, json, threading, random
from datetime import datetime, timezone
from Crypto.Cipher import DES, DES3

HOST = os.getenv("JPOS_HOST", "localhost")
PORT = int(os.getenv("JPOS_PORT", "8583"))
TPDU = b"\x60\x00\x00\x00\x00"

BDK = bytes.fromhex(os.environ["JPOS_BDK_HEX"])
MAC_KEY = bytes.fromhex(os.environ["JPOS_MAC_KEY_HEX"])
VARIANT_RIGHT_HALF = bytes.fromhex("C0C0C0C000000000")

STATE_FILE = "terminal_state.json"

TERMINALS = [
    {"tid": "TERM0001", "ksn_base": "FFFF9876543210E00000"},
    {"tid": "TERM0002", "ksn_base": "FFFF9876543211E00000"},
    {"tid": "TERM0003", "ksn_base": "FFFF9876543212E00000"},
]

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {t["tid"]: {"counter": 1} for t in TERMINALS}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def xor(a,b): return bytes(x^y for x,y in zip(a,b))
def des_enc(k,d): return DES.new(k, DES.MODE_ECB).encrypt(d)
def des_dec(k,d): return DES.new(k, DES.MODE_ECB).decrypt(d)

def tdes_enc(k,d):
    return DES3.new(k[:16]+k[:8], DES3.MODE_ECB).encrypt(d)

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

# ✅ FIXED MAC (24-byte key)
def mac_x919(key, data):
    k1 = key[:8]
    k2 = key[8:16]

    padded = data + (b"\x00" * ((8 - len(data) % 8) % 8))
    state = b"\x00" * 8

    for i in range(0, len(padded), 8):
        block = padded[i:i+8]
        state = des_enc(k1, xor(state, block))

    state = DES.new(k2, DES.MODE_ECB).decrypt(state)
    state = DES.new(k1, DES.MODE_ECB).encrypt(state)

    return state

def bcd_pack(s):
    if len(s)%2:
        raise ValueError(f"bcd_pack requires even length, got {len(s)} for '{s}'")
    return bytes.fromhex(s)

def bcd_pack_right_padded(s):
    if len(s)%2:
        s = s + "0"
    return bytes.fromhex(s)

def pack_num(v, d):
    v=v.zfill(d)
    return bcd_pack_right_padded(v)

def pack_llnum(v):
    l=f"{len(v):02}"
    return bytes.fromhex(l)+bcd_pack_right_padded(v)

def pack_lll(v):
    return f"{len(v):03}".encode()+v.encode()

def pack_msg(fields, macv=None):
    fset = set(fields)
    if macv: fset.add(64)

    bmp=0
    for f in fset:
        bmp |= (1<<(64-f))

    data = bcd_pack("0200") + bmp.to_bytes(8,"big")

    for f in sorted(fset):
        if f==64:
            data+=macv
            continue

        v=fields[f]

        if f==2:
            data+=pack_llnum(v)
        elif f in [3,4,7,11,12,13,22,25,49]:
            lens={3:6,4:12,7:10,11:6,12:6,13:4,22:3,25:2,49:3}
            data+=pack_num(v,lens[f])
        elif f in [41,42]:
            lens={41:8,42:15}
            data+=v.encode().ljust(lens[f],b" ")
        elif f==52:
            data+=v
        elif f==62:
            data+=pack_lll(v)

    return data

def send(msg):
    with socket.socket() as s:
        s.connect((HOST, PORT))
        s.sendall(msg)
        return s.recv(4096)

def get_response_code(resp):
    if len(resp) < 2 + 5 + 2 + 8:
        raise ValueError("Response too short")

    payload = resp[2:]
    iso = payload[5:]

    offset = 0
    offset += 2  # MTI BCD
    bitmap = int.from_bytes(iso[offset:offset + 8], "big")
    offset += 8

    fields = [f for f in range(1, 65) if bitmap & (1 << (64 - f))]

    def parse_llnum_len(first_byte):
        return ((first_byte >> 4) & 0x0F) * 10 + (first_byte & 0x0F)

    for f in fields:
        if f == 1:
            continue
        if f == 2:
            pan_len = parse_llnum_len(iso[offset])
            offset += 1
            offset += (pan_len + 1) // 2
        elif f == 3:
            offset += 3
        elif f == 4:
            offset += 6
        elif f == 7:
            offset += 5
        elif f == 11:
            offset += 3
        elif f == 12:
            offset += 3
        elif f == 13:
            offset += 2
        elif f == 22:
            offset += 2
        elif f == 25:
            offset += 1
        elif f == 39:
            b = iso[offset]
            return f"{(b >> 4) & 0x0F}{b & 0x0F}"
        elif f == 41:
            offset += 8
        elif f == 42:
            offset += 15
        elif f == 49:
            offset += 2
        elif f == 52:
            offset += 8
        elif f == 54:
            lll = iso[offset:offset + 3]
            data_len = int(lll.decode("ascii"))
            offset += 3 + data_len
        elif f == 62:
            lll = iso[offset:offset + 3]
            data_len = int(lll.decode("ascii"))
            offset += 3 + data_len
        elif f == 64:
            offset += 8
        else:
            raise ValueError(f"Unsupported field in parser: {f}")

    raise ValueError("Field 39 not found")

def build_ksn(base, counter):
    b = bytearray(bytes.fromhex(base))
    b[-3:] = counter.to_bytes(3,"big")
    return b.hex().upper()

def run_term(term, state, with_mac):
    tid, base = term["tid"], term["ksn_base"]

    for _ in range(3):
        c = state[tid]["counter"]
        ksn = build_ksn(base, c)
        state[tid]["counter"] += 1

        pan="4111111111111111"
        now = datetime.now(timezone.utc)
        key = derive_pin_key(BDK, ksn)

        fields = {
            2: pan,
            3:"000000",
            4:"000000010000",
            7: now.strftime("%m%d%H%M%S"),
            11: str(random.randint(0, 999999)).zfill(6),
            12: now.strftime("%H%M%S"),
            13: now.strftime("%m%d"),
            22:"051",
            25:"00",
            41: tid,
            42:"MERCHANT000001",
            49:"840",
            62: ksn,
            52: build_pin("1234", pan, key)
        }

        macv=None
        if with_mac:
            temp = pack_msg(fields, macv=b"\x00"*8)
            macv = mac_x919(MAC_KEY, temp)

        body = pack_msg(fields, macv)
        full = TPDU + body
        msg = struct.pack(">H", len(full)) + full

        resp = send(msg)
        rc = get_response_code(resp)
        print(f"[{tid}] RC={rc}")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--with-mac", action="store_true")
    args=ap.parse_args()

    state = load_state()

    threads=[]
    for t in TERMINALS:
        th=threading.Thread(target=run_term, args=(t,state,args.with_mac))
        th.start()
        threads.append(th)

    for th in threads:
        th.join()

    save_state(state)

if __name__=="__main__":
    main()
