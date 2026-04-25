#!/usr/bin/env python3

import socket
import struct
from datetime import datetime
from Crypto.Cipher import DES, DES3

HOST = "localhost"
PORT = 8583

TPDU = b"\x60\x00\x00\x00\x00"

BDK = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
KSN = bytes.fromhex("FFFF9876543210E00001")
VARIANT_RIGHT_HALF = bytes.fromhex("C0C0C0C000000000")
MAC_KEY = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")


def bcd_pack(s: str) -> bytes:
    if len(s) % 2 != 0:
        s = "0" + s
    return bytes.fromhex(s)


def bcd_pack_right_padded(s: str, pad_nibble: str = "0") -> bytes:
    if len(s) % 2 != 0:
        s = s + pad_nibble
    return bytes.fromhex(s)


def pack_ifb_numeric(value: str, digits: int) -> bytes:
    if not value.isdigit():
        raise ValueError(f"Numeric field contains non-digits: {value!r}")
    if len(value) > digits:
        raise ValueError(f"Numeric field too long: {value!r} > {digits}")
    return bcd_pack_right_padded(value.zfill(digits))


def pack_ifb_llnum(value: str) -> bytes:
    if not value.isdigit():
        raise ValueError(f"LLNUM field contains non-digits: {value!r}")
    if len(value) > 99:
        raise ValueError(f"LLNUM field too long: {len(value)}")
    return bcd_pack(f"{len(value):02}") + bcd_pack_right_padded(value)


def pack_ifb_lllchar(value: str) -> bytes:
    value_bytes = value.encode("ascii")
    length = len(value_bytes)
    if length > 999:
        raise ValueError(f"LLLCHAR field too long: {length}")
    # jPOS IFB_LLLCHAR uses a 3-digit BCD length prefix packed into 2 bytes.
    # Example: len=37 -> 0x00 0x37
    return bcd_pack(f"{length:03}") + value_bytes


def pack_ifa_lllchar(value: str) -> bytes:
    value_bytes = value.encode("ascii")
    length = len(value_bytes)
    if length > 999:
        raise ValueError(f"IFA_LLLCHAR field too long: {length}")
    return f"{length:03}".encode("ascii") + value_bytes


def pack_if_char(value: str, length: int) -> bytes:
    value_bytes = value.encode("ascii")
    if len(value_bytes) > length:
        raise ValueError(
            f"CHAR field length mismatch: expected <= {length}, got {len(value_bytes)}"
        )
    return value_bytes.ljust(length, b" ")


def pack_ifb_binary_hex(value: str, length: int) -> bytes:
    raw = bytes.fromhex(value)
    if len(raw) != length:
        raise ValueError(
            f"Binary field length mismatch: expected {length}, got {len(raw)}"
        )
    return raw


def expand_key(k):
    return k + k[:8]


def tdes_encrypt(key, data):
    return DES3.new(expand_key(key), DES3.MODE_ECB).encrypt(data)


def tdes_decrypt(key, data):
    return DES3.new(expand_key(key), DES3.MODE_ECB).decrypt(data)


def des_encrypt(key, data):
    return DES.new(key, DES.MODE_ECB).encrypt(data)


def xor_bytes(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))


def tdes_encrypt_ede(key: bytes, data: bytes) -> bytes:
    left = key[:8]
    right = key[8:]
    return des_encrypt(left, DES.new(right, DES.MODE_ECB).decrypt(des_encrypt(left, data)))


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


def build_pin_block(pin):
    block = f"0{len(pin)}{pin}" + "F" * (16 - len(pin) - 2)
    return bytes.fromhex(block)


def build_pan_block(pan):
    pan12 = pan[-13:-1]
    return bytes.fromhex("0000" + pan12)


def encrypt_pin(pin, pan, pin_key):
    pin_block = build_pin_block(pin)
    pan_block = build_pan_block(pan)
    clear = bytes(a ^ b for a, b in zip(pin_block, pan_block))
    return tdes_encrypt(pin_key, clear)


def retail_mac(key: bytes, data: bytes) -> bytes:
    left = key[:8]
    right = key[8:]
    padded = data + (b"\x00" * ((8 - len(data) % 8) % 8))
    state = b"\x00" * 8

    for offset in range(0, len(padded), 8):
        block = padded[offset:offset + 8]
        state = des_encrypt(left, xor_bytes(state, block))

    state = DES.new(right, DES.MODE_ECB).decrypt(state)
    return des_encrypt(left, state)


def pack_fields(fields: dict[int, str], mac_value: bytes | None = None) -> bytes:
    bitmap = 0
    field_ids = set(fields)
    if mac_value is not None:
        field_ids.add(64)

    for f in field_ids:
        bitmap |= (1 << (64 - f))

    data = bcd_pack("0200") + bitmap.to_bytes(8, "big")

    for f in sorted(field_ids):
        if f == 64:
            data += mac_value
            continue

        v = fields[f]

        if f == 2:
            data += pack_ifb_llnum(v)

        elif f in [3, 4, 7, 11, 12, 13, 22, 25, 49]:
            fixed_lengths = {
                3: 6,
                4: 12,
                7: 10,
                11: 6,
                12: 6,
                13: 4,
                22: 3,
                25: 2,
                49: 3,
            }
            data += pack_ifb_numeric(v, fixed_lengths[f])

        elif f == 35:
            data += pack_ifb_lllchar(v)

        elif f == 62:
            data += pack_ifa_lllchar(v)

        elif f in [41, 42]:
            fixed_lengths = {41: 8, 42: 15}
            data += pack_if_char(v, fixed_lengths[f])

        elif f == 52:
            data += pack_ifb_binary_hex(v, 8)

        else:
            raise ValueError(f"Unsupported field: {f}")

    return data


def build_iso():
    pan = "4111111111111111"
    pin = "1234"

    now = datetime.now()

    fields = {
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
        62: KSN.hex().upper(),
    }

    pin_key = derive_pin_key(BDK, KSN)
    enc_pin = encrypt_pin(pin, pan, pin_key)

    fields[52] = enc_pin.hex().upper()
    mac = retail_mac(MAC_KEY, pack_fields(fields, mac_value=b"\x00" * 8))
    data = pack_fields(fields, mac_value=mac)

    full = TPDU + data
    return struct.pack(">H", len(full)) + full


def send(msg):
    print("\nSENT HEX:")
    print(msg.hex().upper())

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((HOST, PORT))
        s.sendall(msg)
        resp = s.recv(4096)

    print("\nRECEIVED HEX:")
    print(resp.hex().upper())


if __name__ == "__main__":
    msg = build_iso()
    send(msg)
