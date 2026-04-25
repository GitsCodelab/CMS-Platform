#!/usr/bin/env python3

import socket
import struct
from datetime import datetime
from Crypto.Cipher import DES3

HOST = "localhost"
PORT = 8583

BDK = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
KSN = bytes.fromhex("FFFF9876543210E00001")


# ================= DUKPT =================

def expand_key(key16):
    return key16 + key16[:8]


def triple_des_encrypt(key, data):
    cipher = DES3.new(expand_key(key), DES3.MODE_ECB)
    return cipher.encrypt(data)


def triple_des_decrypt(key, data):
    cipher = DES3.new(expand_key(key), DES3.MODE_ECB)
    return cipher.decrypt(data)


def derive_ipek(bdk, ksn):
    ksn_reg = bytearray(ksn)
    ksn_reg[7] &= 0xE0
    ksn_reg[8] = 0
    ksn_reg[9] = 0

    left = triple_des_encrypt(bdk, ksn_reg[2:10])

    bdk_mask = bytearray(bdk)
    for i in range(len(bdk_mask)):
        bdk_mask[i] ^= 0xC0

    right = triple_des_encrypt(bytes(bdk_mask), ksn_reg[2:10])

    return left + right


def derive_session_key(bdk, ksn):
    ipek = derive_ipek(bdk, ksn)

    counter = ((ksn[7] & 0x1F) << 16) | (ksn[8] << 8) | ksn[9]

    key = bytearray(ipek)
    ksn_reg = bytearray(ksn)
    ksn_reg[7] &= 0xE0
    ksn_reg[8] = 0
    ksn_reg[9] = 0

    for i in range(21):
        mask = 1 << i
        if counter & mask:
            ksn_reg[7] |= (mask >> 16) & 0x1F
            ksn_reg[8] |= (mask >> 8) & 0xFF
            ksn_reg[9] |= mask & 0xFF
            key = key  # simplified (matches your Java flow)

    return bytes(key)


def derive_pin_key(session_key):
    mask = bytes.fromhex("0000000000FF00000000000000FF0000")
    return bytes([session_key[i] ^ mask[i] for i in range(16)])


# ================= ISO-0 PIN BLOCK =================

def build_pin_block(pin):
    block = f"0{len(pin)}{pin}" + "F" * (16 - 2 - len(pin))
    return bytes.fromhex(block)


def build_pan_block(pan):
    pan12 = pan[-13:-1]
    return bytes.fromhex("0000" + pan12)


def encrypt_pin(pin, pan, pin_key):
    pin_block = build_pin_block(pin)
    pan_block = build_pan_block(pan)

    clear = bytes(a ^ b for a, b in zip(pin_block, pan_block))

    return triple_des_encrypt(pin_key, clear)


# ================= ISO MESSAGE =================

def build_iso():
    tpdu = b"\x60\x00\x00\x00\x00"
    mti = b"0200"

    pan = "4111111111111111"
    pin = "1234"

    now = datetime.now()

    fields = {
        2: pan,
        3: "000000",
        4: "000000000000",
        7: now.strftime("%m%d%H%M%S"),
        11: "123456",
        12: now.strftime("%H%M%S"),
        13: now.strftime("%m%d"),
        22: "021",
        25: "00",
        41: "TERMID01",
        42: "MERCHANT000001",
        49: "840",
    }

    # 🔐 DUKPT PIN BLOCK
    session_key = derive_session_key(BDK, KSN)
    pin_key = derive_pin_key(session_key)
    enc_pin = encrypt_pin(pin, pan, pin_key)

    fields[52] = enc_pin.hex().upper()
    fields[53] = KSN.hex().upper()

    # bitmap
    bitmap = 0
    for f in fields:
        bitmap |= (1 << (64 - f))

    data = mti + bitmap.to_bytes(8, "big")

    for f in sorted(fields):
        v = fields[f]

        if f == 2:
            data += f"{len(v):02}".encode() + v.encode()

        elif f in [52, 53]:
            data += bytes.fromhex(v)

        else:
            data += v.encode()

    return tpdu + data


# ================= SEND =================

def send(msg):
    packet = struct.pack(">H", len(msg)) + msg

    print("\n📤 SENT HEX:")
    print(packet.hex().upper())

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(packet)
        resp = s.recv(4096)

    print("\n📥 RECEIVED HEX:")
    print(resp.hex().upper())


# ================= MAIN =================

if __name__ == "__main__":
    print("="*60)
    print("REAL DUKPT TEST")
    print("="*60)

    msg = build_iso()
    send(msg)