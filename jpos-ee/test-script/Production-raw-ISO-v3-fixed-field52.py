#!/usr/bin/env python3

import os
import socket
import struct
import argparse
from datetime import datetime
from typing import Optional

from Crypto.Cipher import DES, DES3

HOST = os.getenv("JPOS_HOST", "localhost")
PORT = int(os.getenv("JPOS_PORT", "8583"))
TPDU = b"\x60\x00\x00\x00\x00"

BDK = bytes.fromhex(os.environ["JPOS_BDK_HEX"])
MAC_KEY = bytes.fromhex(os.environ["JPOS_MAC_KEY_HEX"])
# KSN_HEX = os.getenv("JPOS_KSN_HEX", "FFFF9876543210E00001").strip().upper()
KSN_HEX = "FFFF9876543210E00008"
VARIANT_RIGHT_HALF = bytes.fromhex("C0C0C0C000000000")

ALLOWED_FIELDS = {2,3,4,7,11,12,13,22,25,41,42,49,52,62}

def bcd_pack(s: str) -> bytes:
    if len(s) % 2 != 0:
        raise ValueError(f"bcd_pack requires even length, got {len(s)} for '{s}'")
    return bytes.fromhex(s)

def bcd_pack_right_padded(s: str, pad_nibble: str = "0") -> bytes:
    if len(s) % 2 != 0:
        s = s + pad_nibble
    return bytes.fromhex(s)

def pack_ifb_numeric(value: str, digits: int) -> bytes:
    return bcd_pack_right_padded(value.zfill(digits))

def pack_ifb_llnum(value: str) -> bytes:
    return bcd_pack(f"{len(value):02}") + bcd_pack_right_padded(value)

def pack_ifa_lllchar(value: str) -> bytes:
    return f"{len(value):03}".encode() + value.encode()

def pack_if_char(value: str, length: int) -> bytes:
    return value.encode().ljust(length, b" ")

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def des_encrypt(key: bytes, data: bytes) -> bytes:
    return DES.new(key, DES.MODE_ECB).encrypt(data)

def des_decrypt(key: bytes, data: bytes) -> bytes:
    return DES.new(key, DES.MODE_ECB).decrypt(data)

# def tdes_encrypt(key: bytes, data: bytes) -> bytes:
#     return DES3.new(key + key[:8], DES3.MODE_ECB).encrypt(data)
def tdes_encrypt(key: bytes, data: bytes) -> bytes:
    return DES3.new(key[:16] + key[:8], DES3.MODE_ECB).encrypt(data)

def tdes_encrypt_ede(key: bytes, data: bytes) -> bytes:
    left = key[:8]
    right = key[8:16]
    return des_encrypt(left, des_decrypt(right, des_encrypt(left, data)))

def shift_right_21(counter_bytes: bytearray) -> None:
    carry = 0
    for idx in range(len(counter_bytes)):
        new_carry = counter_bytes[idx] & 0x01
        counter_bytes[idx] = ((counter_bytes[idx] >> 1) | (carry << 7)) & 0xFF
        carry = new_carry

def derive_pin_key(bdk: bytes, ksn_hex: str) -> bytes:
    ksn = bytes.fromhex(ksn_hex)

    padded_ksn_hex = ksn.hex().upper().rjust(20, "F")
    initial_ksn = bytearray(bytes.fromhex(padded_ksn_hex[:16]))
    initial_ksn[7] &= 0xE0

    left_bdk = bdk[:8]
    right_bdk = bdk[8:16]

    current_key = bytearray(
        tdes_encrypt_ede(bdk[:16], bytes(initial_ksn))
        + tdes_encrypt_ede(
            xor_bytes(left_bdk, VARIANT_RIGHT_HALF) + xor_bytes(right_bdk, VARIANT_RIGHT_HALF),
            bytes(initial_ksn),
        )
    )

    ksn_bytes = bytearray(bytes.fromhex(ksn.hex().upper()[-16:]))
    ksn_bytes[4] &= 0xE0

    transaction_counter = bytearray(ksn[-3:])
    transaction_counter[0] &= 0x1F
    shift_reg = bytearray(bytes.fromhex("100000"))

    while any(shift_reg):
        if any((shift_reg[i] & transaction_counter[i]) != 0 for i in range(3)):
            left = bytes(current_key[:8])
            right = bytes(current_key[8:16])

            for i in range(3):
                ksn_bytes[5 + i] |= shift_reg[i]

            crypto_reg_1 = xor_bytes(bytes(ksn_bytes), right)
            crypto_reg_1 = des_encrypt(left, crypto_reg_1)
            crypto_reg_1 = xor_bytes(crypto_reg_1, right)

            left_variant = xor_bytes(left, VARIANT_RIGHT_HALF)
            right_variant = xor_bytes(right, VARIANT_RIGHT_HALF)

            crypto_reg_2 = xor_bytes(bytes(ksn_bytes), right_variant)
            crypto_reg_2 = des_encrypt(left_variant, crypto_reg_2)
            crypto_reg_2 = xor_bytes(crypto_reg_2, right_variant)

            current_key = bytearray(crypto_reg_2 + crypto_reg_1)

        shift_right_21(shift_reg)

    current_key[7] ^= 0xFF
    current_key[15] ^= 0xFF
    return bytes(current_key)

def build_pin_block(pin: str) -> bytes:
    return bytes.fromhex(f"0{len(pin)}{pin}" + "F" * (16 - len(pin) - 2))

def build_pan_block(pan: str) -> bytes:
    return bytes.fromhex("0000" + pan[-13:-1])

def encrypt_pin(pin: str, pan: str, key: bytes) -> bytes:
    clear = xor_bytes(build_pin_block(pin), build_pan_block(pan))
    return tdes_encrypt(key, clear)

def retail_mac_ansi_x919(key: bytes, data: bytes) -> bytes:
    left = key[:8]
    right = key[8:16]
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
    stan = now.strftime("%H%M%S")

    assert len(KSN_HEX) == 20

    dukpt_key = derive_pin_key(BDK, KSN_HEX)

    fields = {
        2: pan,
        3: "000000",
        4: "000000010000",
        7: now.strftime("%m%d%H%M%S"),
        11: stan,
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
    return resp

def get_response_code(resp: bytes) -> str:
    if len(resp) < 2 + 5 + 2 + 8:
        raise ValueError("Response too short")

    payload = resp[2:]
    iso = payload[5:]

    offset = 0
    offset += 2  # MTI BCD (2 bytes)
    bitmap = int.from_bytes(iso[offset:offset + 8], "big")
    offset += 8

    fields = [f for f in range(1, 65) if bitmap & (1 << (64 - f))]

    def parse_llnum_len(first_byte: int) -> int:
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

    raise ValueError("Field 39 not found in response")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send 0200 ISO message to jPOS and validate response")
    parser.add_argument("--with-mac", action="store_true", help="Send request with field 64")
    parser.add_argument("--no-mac", action="store_true", help="Send request without field 64")
    args = parser.parse_args()

    include_mac = os.getenv("JPOS_REQUIRE_MAC", "false").strip().lower() == "true"
    if args.with_mac:
        include_mac = True
    if args.no_mac:
        include_mac = False

    print(f"MAC MODE: {'ON' if include_mac else 'OFF'}")
    resp = send(build_message(include_mac=include_mac))

    rc = get_response_code(resp)
    print(f"\nPARSED RC (field 39): {rc}")

    if rc != "00":
        raise SystemExit(f"Unexpected response code: {rc} (expected 00)")

    print("E2E OK: response code is 00")
