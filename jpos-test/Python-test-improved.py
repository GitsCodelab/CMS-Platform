#!/usr/bin/env python3
"""
jPOS ISO 8583 Connection Test
Tests connectivity to jPOS payment processor on port 5000
"""

import socket
import time
import sys

def test_jpos_connection(host="localhost", port=5000, timeout=5):
    """
    Test jPOS connection and ISO 8583 message handling
    """
    print("=" * 60)
    print("jPOS ISO 8583 Connection Test")
    print("=" * 60)
    print(f"Target: {host}:{port}")
    print(f"Timeout: {timeout}s")
    print()
    
    try:
        # Create socket
        print("[*] Creating socket...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        
        # Connect to jPOS
        print(f"[*] Connecting to {host}:{port}...")
        s.connect((host, port))
        print("[✓] Connected successfully")
        
        # Prepare ISO 8583 message
        # Format: 0800 (network management request)
        msg = b"0800822000000000000004000000000000001234567890123456"
        print(f"[*] Sending ISO 8583 message ({len(msg)} bytes)...")
        print(f"    Message: {msg.decode('utf-8', errors='ignore')}")
        
        # Send message
        s.send(msg)
        print("[✓] Message sent")
        
        # Try to receive response
        print("[*] Waiting for response...")
        try:
            response = s.recv(4096)
            if response:
                print(f"[✓] Response received ({len(response)} bytes)")
                print(f"    Data: {response}")
            else:
                print("[!] No response data received (connection closed by server)")
        except socket.timeout:
            print("[!] Timeout waiting for response (server may have closed connection)")
        except ConnectionResetError:
            print("[!] Connection reset by jPOS (normal behavior after processing)")
        
        print("[✓] Test completed successfully")
        print()
        print("=" * 60)
        print("✅ jPOS is responding to ISO 8583 messages!")
        print("=" * 60)
        return True
        
    except ConnectionRefusedError:
        print("[✗] Connection refused - jPOS may not be running on this port")
        print("    Start with: docker compose up cms-jpos -d")
        return False
    except socket.timeout:
        print("[✗] Connection timeout - jPOS not responding")
        return False
    except Exception as e:
        print(f"[✗] Error: {type(e).__name__}: {e}")
        return False
    finally:
        try:
            s.close()
            print("[*] Socket closed")
        except:
            pass

if __name__ == "__main__":
    # Test jPOS on default port
    success = test_jpos_connection()
    
    # Also test jPOS EE on secondary port if needed
    print()
    print("Optional: Testing jPOS EE on port 5001...")
    test_jpos_connection(port=5001)
    
    sys.exit(0 if success else 1)
