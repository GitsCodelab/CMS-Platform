#!/usr/bin/env python3
"""
Debug test to inspect raw ISO 8583 message/response bytes
"""

import socket
import struct
from datetime import datetime

TPDU = b"\x60\x00\x00\x00\x00"

def build_0100_debug():
    """Build simple authorization request for debugging"""
    pan = "4111111111111111"
    amount = "10000"
    stan = "100001"
    now = datetime.now()
    
    # Fields: 2, 3, 4, 7, 11, 12, 13, 22, 25, 35, 41, 42, 49, 52, 55
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
    
    # Build bitmap
    bitmap = 0
    for f in fields:
        bitmap |= (1 << (64 - f))
    
    bitmap_bytes = bitmap.to_bytes(8, "big")
    mti = "0100"
    
    # Build message
    data = mti.encode() + bitmap_bytes
    
    for f in sorted(fields):
        v = fields[f]
        if f == 2:  # PAN LLVAR
            data += str(len(v)).zfill(2).encode() + v.encode()
        elif f == 35:  # Track 2 LLVAR
            data += str(len(v)).zfill(2).encode() + v.encode()
        elif f == 52:  # PIN Block BINARY
            data += v
        elif f == 55:  # EMV LLLVAR
            data += str(len(v)).zfill(3).encode() + v
        else:  # Fixed fields
            data += v.encode() if isinstance(v, str) else v
    
    full_msg = TPDU + data
    msg = struct.pack(">H", len(full_msg)) + full_msg
    
    print("=" * 70)
    print("REQUEST: Authorization (0100)")
    print("=" * 70)
    print(f"Raw HEX: {msg.hex().upper()}")
    print(f"Message Length: {len(msg)} bytes")
    print(f"Payload: {len(full_msg)} bytes")
    print()
    
    return msg

def send_and_analyze(msg):
    """Send message and show response analysis"""
    try:
        sock = socket.socket()
        sock.connect(("localhost", 8583))
        sock.sendall(msg)
        resp = sock.recv(4096)
        sock.close()
        
        print("=" * 70)
        print("RESPONSE")
        print("=" * 70)
        print(f"Raw HEX: {resp.hex().upper()}")
        print(f"Total bytes: {len(resp)}")
        
        if len(resp) >= 2:
            msg_len = struct.unpack(">H", resp[:2])[0]
            print(f"Message length field: {msg_len}")
            
            if len(resp) >= msg_len + 2:
                payload = resp[2:2+msg_len]
                tpdu = payload[:5]
                mti = payload[5:9].decode()
                bitmap_bytes = payload[9:17]
                bitmap = int.from_bytes(bitmap_bytes, "big")
                
                print(f"TPDU: {tpdu.hex().upper()}")
                print(f"MTI: {mti}")
                print(f"Bitmap: {bitmap_bytes.hex().upper()}")
                print(f"Fields present: {bin(bitmap).count('1')}")
                
                # Parse response code (field 39)
                pos = 17
                for field_num in range(2, 65):
                    if bitmap & (1 << (64 - field_num)):
                        if field_num == 39:
                            resp_code = payload[pos:pos+2].decode()
                            print(f"\nField 39 (Response Code): {resp_code}")
                            break
                        else:
                            # Skip to next field
                            if field_num == 2:
                                length = int(payload[pos:pos+2])
                                pos += 2 + length
                            elif field_num == 35:
                                length = int(payload[pos:pos+2])
                                pos += 2 + length
                            elif field_num == 52:
                                pos += 8
                            elif field_num == 55:
                                length = int(payload[pos:pos+3])
                                pos += 3 + length
                            else:
                                # Fixed field lengths
                                lengths = {3:6, 4:12, 7:10, 11:6, 12:6, 13:4, 22:3, 25:2, 37:12, 38:6, 41:8, 42:15, 49:3}
                                if field_num in lengths:
                                    pos += lengths[field_num]
                
        print()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    msg = build_0100_debug()
    send_and_analyze(msg)
