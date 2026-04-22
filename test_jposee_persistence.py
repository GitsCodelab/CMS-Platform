#!/usr/bin/env python3
"""
jPOS-EE Database Verification Script
Purpose: Test if ISO 8583 message was persisted to database after connection
Date: April 22, 2026
"""

import socket
import psycopg2
import time

HOST = "localhost"
PORT = 5001
DB_HOST = "localhost"
DB_PORT = 5433
DB_NAME = "jposee"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

# ISO message
iso_message = "0200F23C448108E0800000000000000000164000000000000000000001000004221030301234561030300422012000123456789012TERMID01MERCHANT000001818"
data = iso_message.encode()
length = len(data)
header = length.to_bytes(2, byteorder='big')

print("=" * 80)
print("jPOS-EE Database Persistence Test")
print("=" * 80)
print(f"ISO Message: {iso_message[:50]}...")
print("-" * 80)

# First, check database before sending
print("\n[1] Checking database BEFORE sending ISO message...")
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM iso_transactions")
    count_before = cursor.fetchone()[0]
    print(f"✅ Database connected. Current transaction count: {count_before}")
    conn.close()
except Exception as e:
    print(f"❌ Database error: {e}")
    exit(1)

# Send ISO message
print(f"\n[2] Sending ISO message to {HOST}:{PORT}...")
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((HOST, PORT))
        s.sendall(header + data)
        print("✅ ISO message sent!")
        
        # Try to receive response (optional - don't fail if no response)
        try:
            response = s.recv(4096)
            print(f"✅ Response received: {len(response)} bytes")
        except socket.timeout:
            print("⚠️  No response received (timeout) - this is OK")
        except ConnectionResetError:
            print("⚠️  Connection reset by peer - message may still be persisted")
except Exception as e:
    print(f"❌ Connection error: {e}")
    exit(1)

# Wait a moment for database to commit
time.sleep(2)

# Check database after sending
print(f"\n[3] Checking database AFTER sending ISO message...")
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM iso_transactions")
    count_after = cursor.fetchone()[0]
    print(f"✅ Database connected. Transaction count after: {count_after}")
    
    if count_after > count_before:
        print(f"\n✅ SUCCESS! Message was persisted!")
        print(f"   New transactions: {count_after - count_before}")
        
        # Get the latest transaction details
        cursor.execute("""
            SELECT id, mti, amount, status, created_at 
            FROM iso_transactions 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()
        if row:
            print(f"\n   Latest transaction:")
            print(f"   - ID: {row[0]}")
            print(f"   - MTI: {row[1]}")
            print(f"   - Amount: {row[2]}")
            print(f"   - Status: {row[3]}")
            print(f"   - Created: {row[4]}")
    else:
        print(f"\n⚠️  No new transactions persisted (before: {count_before}, after: {count_after})")
    
    conn.close()
except Exception as e:
    print(f"❌ Database error: {e}")
    exit(1)

print("\n" + "=" * 80)
