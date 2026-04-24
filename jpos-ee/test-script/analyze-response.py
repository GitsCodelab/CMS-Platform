#!/usr/bin/env python3
"""
Enhanced debug to show all fields in responses
"""

import socket
import struct
from datetime import datetime

TPDU = b"\x60\x00\x00\x00\x00"

def build_auth():
    """Build authorization request"""
    pan = "4111111111111111"
    amount = "10000"
    stan = "100001"
    now = datetime.now()
    
    fields = {
        2: pan,
        3: "000000",
        4: amount.zfill(12),
        7: now.strftime("%m%d%H%M%S"),
        11: stan.zfill(6),
        12: now.strftime("%H%M%S"),
        13: now.strftime("%m%d"),
        22: "021",
        25: "00",
        35: f"{pan}=25122010000000000000",
        41: "TERMID01",
        42: "MERCHANT0000010",
        49: "840",
        52: bytes.fromhex("1234FFFFFFFFFFFF"),
        55: bytes.fromhex("9F2608A1A2A3A4A5A6A7"),
    }
    
    bitmap = 0
    for f in fields:
        bitmap |= (1 << (64 - f))
    
    bitmap_bytes = bitmap.to_bytes(8, "big")
    mti = "0100"
    data = mti.encode() + bitmap_bytes
    
    for f in sorted(fields):
        v = fields[f]
        if f in [2, 35]:  # LLVAR
            data += str(len(v)).zfill(2).encode() + v.encode()
        elif f == 52:  # BINARY
            data += v
        elif f == 55:  # LLLVAR
            data += str(len(v)).zfill(3).encode() + v
        else:
            data += v.encode() if isinstance(v, str) else v
    
    full_msg = TPDU + data
    return struct.pack(">H", len(full_msg)) + full_msg

def analyze_response(resp_bytes):
    """Analyze response structure"""
    if len(resp_bytes) < 2:
        print("Response too short")
        return
    
    msg_len = struct.unpack(">H", resp_bytes[:2])[0]
    payload = resp_bytes[2:2+msg_len]
    
    print(f"Total bytes received: {len(resp_bytes)}")
    print(f"Message length field: {msg_len}")
    print(f"Payload size: {len(payload)}")
    print(f"Response HEX: {resp_bytes.hex().upper()}")
    print()
    
    if len(payload) < 17:
        print("Payload too short")
        return
    
    tpdu = payload[:5]
    mti = payload[5:9].decode()
    bitmap_bytes = payload[9:17]
    bitmap = int.from_bytes(bitmap_bytes, "big")
    
    print(f"TPDU: {tpdu.hex().upper()}")
    print(f"MTI: {mti}")
    print(f"Bitmap: {bitmap_bytes.hex().upper()}")
    print(f"Bitmap (binary): {bin(bitmap)}")
    
    # List which fields are present
    fields_present = []
    for i in range(2, 65):
        if bitmap & (1 << (64 - i)):
            fields_present.append(i)
    
    print(f"Fields present: {fields_present}")
    print()
    
    # Parse all fields in order
    pos = 17
    field_lengths = {
        2: ("LLVAR", None),
        3: ("FIXED", 6),
        4: ("FIXED", 12),
        7: ("FIXED", 10),
        11: ("FIXED", 6),
        12: ("FIXED", 6),
        13: ("FIXED", 4),
        22: ("FIXED", 3),
        25: ("FIXED", 2),
        35: ("LLVAR", None),
        37: ("FIXED", 12),
        38: ("FIXED", 6),
        39: ("FIXED", 2),
        41: ("FIXED", 8),
        42: ("FIXED", 15),
        49: ("FIXED", 3),
        52: ("BINARY", 8),
        54: ("LLVAR", None),
        55: ("LLLVAR", None),
    }
    
    for field_num in fields_present:
        if field_num not in field_lengths:
            print(f"Field {field_num}: Unknown type")
            break
        
        ftype, flen = field_lengths[field_num]
        
        if pos >= len(payload):
            print(f"Field {field_num}: Position {pos} exceeds payload {len(payload)}")
            break
        
        print(f"Field {field_num} ({ftype:8s}) @ pos {pos:2d}: ", end="")
        
        if ftype == "FIXED":
            if pos + flen > len(payload):
                print(f"NOT ENOUGH BYTES (need {flen}, have {len(payload)-pos})")
                break
            value = payload[pos:pos+flen].decode(errors='replace')
            print(f"'{value}'")
            pos += flen
        elif ftype == "LLVAR":
            if pos + 2 > len(payload):
                print("NOT ENOUGH BYTES FOR LENGTH")
                break
            length = int(payload[pos:pos+2])
            if pos + 2 + length > len(payload):
                print(f"NOT ENOUGH BYTES (length={length}, have {len(payload)-pos-2})")
                break
            value = payload[pos+2:pos+2+length].decode(errors='replace')
            print(f"(len={length}) '{value}'")
            pos += 2 + length
        elif ftype == "LLLVAR":
            if pos + 3 > len(payload):
                print("NOT ENOUGH BYTES FOR LENGTH")
                break
            length = int(payload[pos:pos+3])
            if pos + 3 + length > len(payload):
                print(f"NOT ENOUGH BYTES (length={length}, have {len(payload)-pos-3})")
                break
            value = payload[pos+3:pos+3+length].hex().upper()
            print(f"(len={length}) {value}")
            pos += 3 + length
        elif ftype == "BINARY":
            if pos + flen > len(payload):
                print(f"NOT ENOUGH BYTES (need {flen})")
                break
            value = payload[pos:pos+flen].hex().upper()
            print(f"{value}")
            pos += flen
    
    if pos < len(payload):
        print(f"\nWarning: {len(payload)-pos} bytes remaining unparse at position {pos}")
        print(f"Remaining HEX: {payload[pos:].hex().upper()}")

if __name__ == "__main__":
    msg = build_auth()
    
    print("=" * 70)
    print("Sending Authorization (0100)")
    print("=" * 70)
    print(f"Request HEX: {msg.hex().upper()}")
    print(f"Request size: {len(msg)} bytes")
    print()
    
    sock = socket.socket()
    sock.connect(("localhost", 8583))
    sock.sendall(msg)
    resp = sock.recv(4096)
    sock.close()
    
    print("=" * 70)
    print("Response Analysis")
    print("=" * 70)
    analyze_response(resp)
