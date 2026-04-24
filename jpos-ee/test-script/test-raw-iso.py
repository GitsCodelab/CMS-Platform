#!/usr/bin/env python3
"""
Direct raw ISO 8583 message test using binary format
Sends properly formatted binary ISO messages to the gateway
"""

import socket
import struct
from datetime import datetime


HOST = "localhost"
PORT = 8583


def send_raw_iso(binary_message: bytes):
    """Send raw binary ISO message and receive response"""
    # Add 2-byte length header (big-endian)
    msg = struct.pack(">H", len(binary_message)) + binary_message

    print("\n📤 SENT (HEX):")
    print(msg.hex().upper())
    print(f"Length: {len(msg)} bytes")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(msg)
        resp = s.recv(4096)

        print("\n📥 RECEIVED (HEX):")
        print(resp.hex().upper())
        print(f"Length: {len(resp)} bytes")

        return resp


def quick_decode(resp: bytes):
    """Basic ISO message decoder"""
    try:
        length = struct.unpack(">H", resp[:2])[0]
        msg = resp[2:2 + length]

        if len(msg) < 17:
            print("Message too short for decoding")
            return

        tpdu = msg[:5].hex().upper()
        mti = msg[5:9].decode()
        bitmap = msg[9:17].hex().upper()

        print("\n🔍 BASIC DECODE:")
        print(f"TPDU   : {tpdu}")
        print(f"MTI    : {mti}")
        print(f"Bitmap : {bitmap}")

    except Exception as e:
        print(f"Decode error: {e}")


def build_balance_inquiry():
    """Build a proper balance inquiry (0200) message"""
    
    # Message components
    tpdu = b"\x60\x00\x00\x00\x00"
    mti = "0200"
    pan = "4111111111111111"
    
    # Fields to include
    fields = {}
    fields[2] = pan
    fields[3] = "000000"  # Processing code
    fields[4] = "000000000000"  # Amount (12 bytes)
    fields[7] = datetime.now().strftime("%m%d%H%M%S")
    fields[11] = "123456"  # STAN
    fields[12] = datetime.now().strftime("%H%M%S")
    fields[13] = datetime.now().strftime("%m%d")
    fields[22] = "021"  # POS entry mode
    fields[25] = "00"   # Function code
    fields[35] = pan + "=25122010000000000000"  # Track 2
    fields[41] = "TERMID01"
    fields[42] = "MERCHANT0000010"
    fields[49] = "840"  # Currency code
    
    # Build bitmap
    bitmap = 0
    for f in fields:
        bitmap |= (1 << (64 - f))
    
    # Build message
    data = mti.encode() + bitmap.to_bytes(8, "big")
    
    # Add fields in order
    for f in sorted(fields):
        v = fields[f]
        if f == 2 or f == 35:  # LLVAR fields
            data += str(len(v)).zfill(2).encode() + v.encode()
        else:
            data += v.encode()
    
    # Combine all
    return tpdu + data


def main():
    print("=" * 70)
    print("RAW ISO 8583 BALANCE INQUIRY TEST (0200)")
    print("=" * 70)
    
    # Build and send message
    binary_msg = build_balance_inquiry()
    print(f"Built message: {len(binary_msg)} bytes")
    
    resp = send_raw_iso(binary_msg)
    quick_decode(resp)
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()