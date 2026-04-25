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
KSN = bytes.fromhex(os.getenv("JPOS_KSN_HEX", "FFFF9876543210E00001"))
VARIANT_RIGHT_HALF = bytes.fromhex("C0C0C0C000000000")


def bcd_pack(s: str) -> bytes:
    if len(s) % 2 != 0:
        s = "0" + s
    return bytes.fromhex(s)


def bcd_pack_right_padded(s: str, pad_nibble: str = "0") -> bytes:
    if len(s) % 2 != 0:
        s = s + pad_nibble
    return bytes.fromhex(s)


def pack_ifb_numeric(value: str, digits: int) -> bytes:
    return bcd_pack_right_padded(value.zfill(digits))


def pack_ifb_llnum(value: str) -> bytes:
    return bcd_pack(f"{len(value):02}") + bcd_pack_right_padded(value)


def pack_ifb_lllchar(value: str) -> bytes:
    return bcd_pack(f"{len(value):03}") + value.encode("ascii")


def pack_ifa_lllchar(value: str) -> bytes:
    return f"{len(value):03}".encode("ascii") + value.encode("ascii")


def pack_if_char(value: str, length: int) -> bytes:
    return value.encode("ascii").ljust(length, b" ")


def pack_ifb_binary_hex(value: str, length: int) -> bytes:
    raw = bytes.fromhex(value)
    if len(raw) != length:
        raise ValueError(f"Expected {length} bytes, got {len(raw)}")
    return raw


def des_encrypt(key: bytes, data: bytes) -> bytes:
    return DES.new(key, DES.MODE_ECB).encrypt(data)


def des_decrypt(key: bytes, data: bytes) -> bytes:
    return DES.new(key, DES.MODE_ECB).decrypt(data)


def tdes_encrypt(key: bytes, data: bytes) -> bytes:
    return DES3.new(key + key[:8], DES3.MODE_ECB).encrypt(data)


def xor_bytes(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))


def tdes_encrypt_ede(key: bytes, data: bytes) -> bytes:
    left = key[:8]
    right = key[8:]
    return des_encrypt(left, des_decrypt(right, des_encrypt(left, data)))


def shift_right_21(counter_bytes: bytearray) -> None:
    carry = 0
    for idx in range(len(counter_bytes)):
        new_carry = counter_bytes[idx] & 0x01
        counter_bytes[idx] = ((counter_bytes[idx] >> 1) | (carry << 7)) & 0xFF
        carry = new_carry


def derive_pin_key(bdk: bytes, ksn: bytes) -> bytes:
    ksn_hex = ksn.hex().upper().rjust(20, "F")
    initial_ksn = bytearray(bytes.fromhex(ksn_hex[:16]))
    initial_ksn[7] &= 0xE0

    left_bdk = bdk[:8]
    right_bdk = bdk[8:]

    current_key = bytearray(
        tdes_encrypt_ede(bdk, bytes(initial_ksn))
        + tdes_encrypt_ede(
            xor_bytes(left_bdk, VARIANT_RIGHT_HALF)
            + xor_bytes(right_bdk, VARIANT_RIGHT_HALF),
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
            right = bytes(current_key[8:])

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


def encrypt_pin(pin: str, pan: str, pin_key: bytes) -> bytes:
    clear = xor_bytes(build_pin_block(pin), build_pan_block(pan))
    return tdes_encrypt(pin_key, clear)


def retail_mac_ansi_x919(key: bytes, data: bytes) -> bytes:
    left = key[:8]
    right = key[8:]
    padded = data + (b"\x00" * ((8 - len(data) % 8) % 8))
    state = b"\x00" * 8
    for offset in range(0, len(padded), 8):
        block = padded[offset:offset + 8]
        state = des_encrypt(left, xor_bytes(state, block))
    state = des_decrypt(right, state)
    return des_encrypt(left, state)


def pack_fields(mti: str, fields: dict[int, str], mac_value: Optional[bytes] = None) -> bytes:
    bitmap = 0
    secondary_bitmap = 0
    field_ids = set(fields)
    if mac_value is not None:
        field_ids.add(64)

    for f in field_ids:
        if f <= 64:
            bitmap |= (1 << (64 - f))
        else:
            bitmap |= (1 << 63)
            secondary_bitmap |= (1 << (128 - f))

    data = bcd_pack(mti) + bitmap.to_bytes(8, "big")
    if secondary_bitmap:
        data += secondary_bitmap.to_bytes(8, "big")
    for f in sorted(field_ids):
        if f == 64:
            data += mac_value
            continue

        v = fields[f]
        if f == 2:
            data += pack_ifb_llnum(v)
        elif f in [3, 4, 7, 11, 12, 13, 22, 25, 49, 70]:
            lengths = {3: 6, 4: 12, 7: 10, 11: 6, 12: 6, 13: 4, 22: 3, 25: 2, 49: 3, 70: 3}
            data += pack_ifb_numeric(v, lengths[f])
        elif f == 35:
            data += pack_ifb_lllchar(v)
        elif f == 62:
            data += pack_ifa_lllchar(v)
        elif f in [41, 42]:
            lengths = {41: 8, 42: 15}
            data += pack_if_char(v, lengths[f])
        elif f == 52:
            data += pack_ifb_binary_hex(v, 8)
        else:
            raise ValueError(f"Unsupported field {f}")
    return data


def build_message(
    mti: str = "0200",
    pan: str = "4111111111111111",
    pin: str = "1234",
    ksn: bytes = KSN,
    include_mac: bool = True,
    tamper_mac: bool = False,
    overrides: Optional[dict[int, str]] = None,
) -> bytes:
    now = datetime.now()
    fields: dict[int, str] = {
        2: pan,
        3: "000000",
        4: "000000010000",
        7: now.strftime("%m%d%H%M%S"),
        11: "123456",
        12: now.strftime("%H%M%S"),
        13: now.strftime("%m%d"),
        22: "021",
        25: "00",
        35: f"{pan}=25122010000000000000",
        41: "TERMID01",
        42: "MERCHANT000001",
        49: "840",
        62: ksn.hex().upper(),
    }

    if mti == "0800":
        fields = {
            7: now.strftime("%m%d%H%M%S"),
            11: "654321",
            70: "301",
        }
    else:
        pin_key = derive_pin_key(BDK, ksn)
        fields[52] = encrypt_pin(pin, pan, pin_key).hex().upper()

    if overrides:
        for field, value in overrides.items():
            if value is None and field in fields:
                del fields[field]
            elif value is not None:
                fields[field] = value

    mac = None
    if include_mac:
        mac = retail_mac_ansi_x919(MAC_KEY, pack_fields(mti, fields, mac_value=b"\x00" * 8))
        if tamper_mac:
            mac = bytes([mac[0] ^ 0xFF]) + mac[1:]

    body = pack_fields(mti, fields, mac_value=mac)
    full = TPDU + body
    return struct.pack(">H", len(full)) + full


def send(msg: bytes) -> bytes:
    print("\nSENT HEX:")
    print(msg.hex().upper())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((HOST, PORT))
        s.sendall(msg)
        resp = s.recv(4096)
    print("\nRECEIVED HEX:")
    print(resp.hex().upper())
    return resp


if __name__ == "__main__":
    send(build_message())
