#!/usr/bin/env python3
import os, socket, struct, threading, random, time, json
from datetime import datetime, timezone
from Crypto.Cipher import DES, DES3

HOST = os.getenv("JPOS_HOST", "localhost")
PORT = int(os.getenv("JPOS_PORT", "8583"))
TPDU = b"\x60\x00\x00\x00\x00"

BDK = bytes.fromhex(os.environ["JPOS_BDK_HEX"])
MAC_KEY = bytes.fromhex(os.environ["JPOS_MAC_KEY_HEX"])
VARIANT_RIGHT_HALF = bytes.fromhex("C0C0C0C000000000")

TERMINALS = [
    {"tid": "TERM0001", "ksn_base": "FFFF9876543210E00000"},
    {"tid": "TERM0002", "ksn_base": "FFFF9876543211E00000"},
    {"tid": "TERM0003", "ksn_base": "FFFF9876543212E00000"},
]

transaction_store = {}

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

def build_ksn(base, counter):
    b = bytearray(bytes.fromhex(base))
    b[-3:] = counter.to_bytes(3, "big")
    return b.hex().upper()

def mac_x919(key, data):
    k1, k2 = key[:8], key[8:16]
    padded = data + (b"\x00" * ((8 - len(data) % 8) % 8))
    state = b"\x00" * 8
    for i in range(0, len(padded), 8):
        state = des_enc(k1, xor(state, padded[i:i+8]))
    state = DES.new(k2, DES.MODE_ECB).decrypt(state)
    state = DES.new(k1, DES.MODE_ECB).encrypt(state)
    return state

def send(msg):
    if random.random() < 0.1:
        print("⚠️ TIMEOUT simulated")
        time.sleep(2)
        return None
    with socket.socket() as s:
        s.settimeout(3)
        s.connect((HOST, PORT))
        s.sendall(msg)
        return s.recv(4096)

def get_rc(resp):
    if resp is None:
        return "TIMEOUT"
    payload = resp[2:]
    iso = payload[5:]

    offset = 2
    bitmap = int.from_bytes(iso[offset:offset+8], "big")
    offset += 8

    fields = [f for f in range(1,65) if bitmap & (1<<(64-f))]

    for f in fields:
        if f == 39:
            b = iso[offset]
            return f"{(b>>4)&0xF}{b&0xF}"
        elif f == 2:
            l=((iso[offset]>>4)*10+(iso[offset]&0xF))
            offset+=1+(l+1)//2
        elif f == 3: offset+=3
        elif f == 4: offset+=6
        elif f == 7: offset+=5
        elif f == 11: offset+=3
        elif f == 12: offset+=3
        elif f == 13: offset+=2
        elif f == 22: offset+=2
        elif f == 25: offset+=1
        elif f == 38: offset+=6
        elif f == 41: offset+=8
        elif f == 42: offset+=15
        elif f == 49: offset+=2
        elif f == 52: offset+=8
        elif f == 62:
            l=int(iso[offset:offset+3].decode())
            offset+=3+l
        elif f == 64: offset+=8

    return "??"

def pack_msg(mti, fields, macv=None):
    fset=set(fields)
    if macv: fset.add(64)

    bmp=0
    for f in fset:
        bmp |= (1<<(64-f))

    data=bytes.fromhex(mti)+bmp.to_bytes(8,"big")

    for f in sorted(fset):
        if f==64:
            data+=macv
            continue
        v=fields[f]
        if f==2:
            l=f"{len(v):02}"
            data+=bytes.fromhex(l)+bytes.fromhex(v if len(v)%2==0 else v+"0")
        elif f in [3,4,7,11,12,13,22,25,49]:
            lens={3:6,4:12,7:10,11:6,12:6,13:4,22:3,25:2,49:3}
            val=v.zfill(lens[f])
            if len(val)%2: val+="0"
            data+=bytes.fromhex(val)
        elif f in [41,42]:
            lens={41:8,42:15}
            data+=v.encode().ljust(lens[f],b" ")
        elif f==52:
            data+=v
        elif f==62:
            data+=f"{len(v):03}".encode()+v.encode()

    return data

def send_tx(mti, fields):
    temp = pack_msg(mti, fields, macv=b"\x00"*8)
    mac = mac_x919(MAC_KEY, temp)
    body = pack_msg(mti, fields, mac)
    msg = struct.pack(">H", len(TPDU+body)) + TPDU + body
    resp = send(msg)
    return get_rc(resp)

def run_term(term):
    tid = term["tid"]
    base = term["ksn_base"]
    counter = 1

    for _ in range(5):
        ksn = build_ksn(base, counter)
        counter += 1

        pan = "4111111111111111"
        now = datetime.now(timezone.utc)
        key = derive_pin_key(BDK, ksn)
        stan = str(random.randint(0,999999)).zfill(6)

        transaction_store[stan] = {
            "terminal": tid,
            "status": "STARTED"
        }

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
        print(f"[{tid}] 0100 RC={rc}")

        if rc == "00":
            transaction_store[stan]["status"] = "AUTHORIZED"
        elif rc in ["05","51"]:
            transaction_store[stan]["status"] = "DECLINED"
            continue
        elif rc == "TIMEOUT":
            transaction_store[stan]["status"] = "TIMEOUT"
            print(f"[{tid}] REVERSAL for STAN={stan}")
            send_tx("0400", fields)
            continue

        fields.update({
            52: build_pin("1234", pan, key),
            62: ksn
        })

        rc = send_tx("0200", fields)
        print(f"[{tid}] 0200 RC={rc}")

        if rc == "00":
            transaction_store[stan]["status"] = "COMPLETED"
        else:
            transaction_store[stan]["status"] = "FAILED"
            print(f"[{tid}] REVERSAL for STAN={stan}")
            rev_fields = {k: v for k, v in fields.items() if k not in [52, 62]}
            send_tx("0400", rev_fields)

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
