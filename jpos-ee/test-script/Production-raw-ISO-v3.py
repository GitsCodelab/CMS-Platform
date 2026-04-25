#!/usr/bin/env python3

import os
import socket
import struct
from datetime import datetime
from typing import Optional

from Crypto.Cipher import DES, DES3

HOST = os.getenv("JPOS_HOST", "localhost")
PORT = int(os.getenv("JPOS_PORT", "8583"))
TPDU = b"\x60\x00\x00\x00\x00"

BDK = bytes.fromhex(os.environ["JPOS_BDK_HEX"])
MAC_KEY = bytes.fromhex(os.environ["JPOS_MAC_KEY_HEX"])
KSN_HEX = os.getenv("JPOS_KSN_HEX", "FFFF9876543210E00001").strip().upper()

ALLOWED_FIELDS = {2,3,4,7,11,12,13,22,25,41,42,49,52,62}

def bcd_pack(s: str) -> bytes:
    if len(s) % 2 != 0:
        s = "0" + s
    return bytes.fromhex(s)

def pack_ifb_numeric(value: str, digits: int) -> bytes:
    return bcd_pack(value.zfill(digits))

def pack_ifb_llnum(value: str) -> bytes:
    return bcd_pack(f"{len(value):02}") + bcd_pack(value)

def pack_ifa_lllchar(value: str) -> bytes:
    return f"{len(value):03}".encode() + value.encode()

def pack_if_char(value: str, length: int) -> bytes:
    return value.encode().ljust(length, b" ")

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def des_encrypt(key: bytes, data: bytes) -> bytes:
    return DES.new(key, DES.MODE_ECB).encrypt(data)

def tdes_encrypt(key: bytes, data: bytes) -> bytes:
    return DES3.new(key + key[:8], DES3.MODE_ECB).encrypt(data)

def derive_dukpt_key(bdk: bytes, ksn_hex: str) -> bytes:
    return bdk[:16]

def build_pin_block(pin: str) -> bytes:
    return bytes.fromhex(f"0{len(pin)}{pin}" + "F" * (16 - len(pin) - 2))

def build_pan_block(pan: str) -> bytes:
    return bytes.fromhex("0000" + pan[-13:-1])

def encrypt_pin(pin: str, pan: str, key: bytes) -> bytes:
    clear = xor_bytes(build_pin_block(pin), build_pan_block(pan))
    return tdes_encrypt(key, clear)

def retail_mac_ansi_x919(key: bytes, data: bytes) -> bytes:
    left = key[:8]
    right = key[8:]
    padded = data + (b"\x00" * ((8 - len(data) % 8) % 8))
    state = b"\x00" * 8
    for i in range(0, len(padded), 8):
        block = padded[i:i+8]
        state = des_encrypt(left, xor_bytes(state, block))
    state = DES.new(right, DES.MODE_ECB).decrypt(state)
    return des_encrypt(left, state)

def pack_fields(mti: str, fields: dict[int, object], mac_value: Optional[bytes]=None) -> bytes:
    field_ids = set(fields) & ALLOWED_FIELDS
    if mac_value:
        field_ids.add(64)

    print("FIELDS SENT:", sorted(field_ids))

    bitmap = 0
    for f in field_ids:
        bitmap |= (1 << (64 - f))

    data = bcd_pack(mti) + bitmap.to_bytes(8, "big")

    for f in sorted(field_ids):
        if f == 64:
            data += mac_value
            continue

        v = fields[f]

        if f == 2:
            data += pack_ifb_llnum(v)
        elif f in [3,4,7,11,12,13,22,25,49]:
            lengths = {3:6,4:12,7:10,11:6,12:6,13:4,22:3,25:2,49:3}
            data += pack_ifb_numeric(v, lengths[f])
        elif f in [41,42]:
            lengths = {41:8,42:15}
            data += pack_if_char(v, lengths[f])
        elif f == 52:
            # ✅ FIX: send raw 8 bytes (not hex string)
            data += v
        elif f == 62:
            data += pack_ifa_lllchar(v)
        else:
            raise Exception(f"Unexpected field {f}")

    return data

def build_message(include_mac=False):
    now = datetime.now()
    pan = "4111111111111111"

    assert len(KSN_HEX) == 20

    dukpt_key = derive_dukpt_key(BDK, KSN_HEX)

    fields = {
        2: pan,
        3: "000000",
        4: "000000010000",
        7: now.strftime("%m%d%H%M%S"),
        11: "123456",
        12: now.strftime("%H%M%S"),
        13: now.strftime("%m%d"),
        22: "051",
        25: "00",
        41: "TERMID01",
        42: "MERCHANT000001",
        49: "840",
        62: KSN_HEX,
        # ✅ FIX: keep as bytes
        52: encrypt_pin("1234", pan, dukpt_key)
    }

    mac = None
    if include_mac:
        temp = pack_fields("0200", fields, mac_value=b"\x00"*8)
        mac = retail_mac_ansi_x919(MAC_KEY, temp)

    body = pack_fields("0200", fields, mac_value=mac)
    full = TPDU + body
    return struct.pack(">H", len(full)) + full

def send(msg: bytes):
    print("\nSENT HEX:")
    print(msg.hex().upper())

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(msg)
        resp = s.recv(4096)

    print("\nRECEIVED HEX:")
    print(resp.hex().upper())

if __name__ == "__main__":
    send(build_message(include_mac=False))
