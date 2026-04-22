#!/usr/bin/env python3
"""
jPOS-EE Connection Verification Script
Purpose: Test ISO 8583 message transmission to jPOS-EE listener
Date: April 22, 2026
"""

import socket
import time
import sys

HOST = "localhost"
PORT = 5001

# ISO message (same we generated earlier)
iso_message = "0200F23C448108E0800000000000000000164000000000000000000001000004221030301234561030300422012000123456789012TERMID01MERCHANT000001818"

# Convert to bytes
data = iso_message.encode()

# Optional: Add length header (VERY IMPORTANT for jPOS)
length = len(data)
header = length.to_bytes(2, byteorder='big')

print("=" * 80)
print("jPOS-EE ISO 8583 Connection Test")
print("=" * 80)
print(f"Target: {HOST}:{PORT}")
print(f"ISO Message Length: {length} bytes")
print(f"ISO Message: {iso_message}")
print("-" * 80)

try:
    print(f"\n[1] Connecting to {HOST}:{PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(10)  # 10 second timeout
        s.connect((HOST, PORT))
        print("✅ Connected successfully!")

        print(f"\n[2] Sending ISO message (length header + data)...")
        print(f"    - Length header: {header.hex()} ({length} bytes)")
        print(f"    - ISO message: {data.decode()}")
        
        # Send: length + data
        s.sendall(header + data)
        print("✅ Message sent successfully!")

        print(f"\n[3] Waiting for response...")
        # Receive response
        response = s.recv(4096)
        print(f"✅ Response received! ({len(response)} bytes)")

        print(f"\n[4] Parsing response...")
        # Remove length header
        if len(response) >= 2:
            resp_len = int.from_bytes(response[:2], 'big')
            print(f"    - Response length header: {response[:2].hex()} ({resp_len} bytes)")
            
            if len(response) >= 2 + resp_len:
                resp_msg = response[2:2+resp_len]
                print(f"    - Response message: {resp_msg.decode()}")
                print("\n" + "=" * 80)
                print("✅ SUCCESS: jPOS-EE is responding correctly!")
                print("=" * 80)
            else:
                print(f"⚠️  Incomplete response: expected {resp_len} bytes, got {len(response)-2}")
        else:
            print("⚠️  Response too short (no length header)")

except ConnectionRefusedError:
    print(f"\n❌ ERROR: Connection refused!")
    print(f"   - jPOS-EE may not be running on {HOST}:{PORT}")
    print(f"   - Check if Docker container 'cms-jposee' is running")
    print(f"   - Run: docker-compose up cms-jposee")
    sys.exit(1)

except socket.timeout:
    print(f"\n❌ ERROR: Connection timeout after 10 seconds")
    print(f"   - jPOS-EE may be unresponsive")
    print(f"   - Check jPOS-EE logs: docker logs cms-jposee")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
