#!/usr/bin/env python3

import socket
import struct


HOST = "localhost"
PORT = 8583


def send_raw_iso(hex_message: str):
    # Convert HEX → bytes
    data = bytes.fromhex(hex_message)

    # Add 2-byte length header (big-endian)
    msg = struct.pack(">H", len(data)) + data

    print("\n📤 SENT (HEX):")
    print(msg.hex().upper())

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(msg)

        resp = s.recv(4096)

        print("\n📥 RECEIVED (HEX):")
        print(resp.hex().upper())

        return resp


# ================= OPTIONAL DECODER =================
def quick_decode(resp: bytes):
    try:
        length = struct.unpack(">H", resp[:2])[0]
        msg = resp[2:2 + length]

        tpdu = msg[:5].hex().upper()
        mti = msg[5:9].decode()
        bitmap = msg[9:17].hex().upper()

        print("\n🔍 BASIC DECODE:")
        print(f"TPDU   : {tpdu}")
        print(f"MTI    : {mti}")
        print(f"Bitmap : {bitmap}")

    except Exception as e:
        print("Decode error:", e)


# ================= TEST MESSAGE =================
def main():
    # 🔥 REAL RAW ISO MESSAGE (same structure as ATM)
    # 0200 Financial Request
    raw_iso_hex = (
        "6000000000"        # TPDU
        "0200"              # MTI
        "7238048020C09200"  # Bitmap

        # Field 2 (LLVAR PAN)
        "16" "4111111111111111"

        # Field 3
        "000000"

        # Field 4
        "000000010000"

        # Field 7
        "0424224832"

        # Field 11
        "123456"

        # Field 12
        "224832"

        # Field 13
        "0424"

        # Field 22
        "021"

        # Field 25
        "00"

        # Field 35 (LLVAR Track2)
        "37" "4111111111111111=25122010000000000000"

        # Field 41
        "TERMID01"

        # Field 42 (15 chars)
        "MERCHANT0000010"

        # Field 49
        "840"

        # Field 52 (PIN block 8 bytes)
        "1234FFFFFFFFFFFF"

        # Field 55 (EMV LLLVAR binary)
        "010" "9F2608A1A2A3A4A5A6A7"
    )

    resp = send_raw_iso(raw_iso_hex)
    quick_decode(resp)


if __name__ == "__main__":
    main()