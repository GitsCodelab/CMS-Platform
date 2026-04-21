import socket
import struct
import time

host = "localhost"
port = 5001  # jPOS-EE listener

# Create a proper ISO 8583 network header + message format
# ISO 8583 network header: 2 bytes with message length
# Then the ISO message itself

# Message Type Indicator (MTI): 0100 (Purchase request)
mti = b"0100"

# Bitmap (16 bytes, indicating which fields are present)
# Fields: 2 (PAN), 4 (Amount), 11 (STAN), 39 (Response Code), 41 (Terminal ID)
bitmap = b"\xb2\x20\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

# Fields:
# Field 2: PAN (Variable, length 2 bytes + data)
pan = b"4532123456789123"
field2 = struct.pack(">H", len(pan)) + pan

# Field 4: Amount (12 bytes)
amount = b"000000015075"  # $150.75

# Field 11: STAN (6 bytes, right-aligned with zeros)
stan = b"123456"

# Field 39: Response Code (2 bytes)
response_code = b"00"

# Field 41: Terminal ID (8 bytes, left-aligned with spaces)
terminal_id = b"ATM001  "

# Build the ISO message
iso_msg = mti + bitmap + field2 + amount + stan + response_code + terminal_id

# Add network header (2 bytes indicating message length)
msg_length = len(iso_msg)
header = struct.pack(">H", msg_length)
full_msg = header + iso_msg

print(f"[*] Connecting to {host}:{port}")
print(f"[*] Message length: {msg_length}")
print(f"[*] Sending ISO message...")
print(f"[*] MTI: {mti.decode()}")
print(f"[*] PAN: {pan.decode()}")
print(f"[*] Amount: {amount.decode()}")
print(f"[*] STAN: {stan.decode()}")
print()

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect((host, port))
    
    s.sendall(full_msg)
    print("[+] Message sent!")
    
    # Receive response
    response_header = s.recv(2)
    if response_header:
        resp_len = struct.unpack(">H", response_header)[0]
        print(f"[+] Response length: {resp_len}")
        
        response = s.recv(resp_len)
        print(f"[+] Response received ({len(response)} bytes)")
        print(f"[+] Response (hex): {response.hex()}")
        print(f"[+] Response (text): {response}")
        
        # Parse response MTI
        if len(response) >= 4:
            resp_mti = response[:4].decode(errors='ignore')
            print(f"[+] Response MTI: {resp_mti}")
    
    s.close()
    print("\n[✓] Test completed successfully")
    
except ConnectionRefusedError:
    print(f"[!] Connection refused - jPOS may not be listening on {host}:{port}")
except socket.timeout:
    print(f"[!] Socket timeout - no response from server")
except ConnectionResetError as e:
    print(f"[!] Connection reset by peer: {e}")
except Exception as e:
    print(f"[!] Error: {e}")
    import traceback
    traceback.print_exc()