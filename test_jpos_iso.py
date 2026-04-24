#!/usr/bin/env python3
"""
ISO 8583 Message Tester for jPOS-EE Gateway
Tests Visa and MasterCard payment transactions via ISO 8583 protocol
"""

import socket
import struct
import json
import sys
from datetime import datetime
from typing import Dict, Tuple


class ISO8583Packager:
    """Simple ISO 8583:1987 message packer/unpacker"""
    
    # Bitmap for tracking which fields are present
    FIELD_LENGTH = {
        1: 16,   # Bitmap (extended)
        2: 19,   # Primary Account Number (PAN)
        3: 6,    # Processing Code
        4: 12,   # Amount
        5: 12,   # Settlement Amount
        11: 6,   # STAN (System Trace Audit Number)
        12: 6,   # Time
        13: 4,   # Date
        14: 4,   # Expiration Date
        15: 4,   # Settlement Date
        39: 2,   # Response Code
        38: 6,   # Authorization Code
        54: 16,  # Balance
    }
    
    @staticmethod
    def build_authorization_request(
        pan: str,
        amount: str,
        stan: str,
        card_type: str = "Visa"
    ) -> bytes:
        """Build ISO 8583 0x0100 (Authorization Request)"""
        # MTI: 0100 (Authorization Request)
        mti = "0100"
        
        # Processing Code: 000000 (Purchase)
        processing_code = "000000"
        
        # Build field values
        fields = {
            2: pan,                    # PAN
            3: processing_code,        # Processing Code
            4: amount.zfill(12),      # Amount
            11: stan.zfill(6),        # STAN
            12: datetime.now().strftime("%H%M%S"),  # Time
            13: datetime.now().strftime("%m%d"),    # Date
            39: "00",                  # Response Code (placeholder)
            38: "123456",              # Auth Code (placeholder)
        }
        
        return ISO8583Packager._build_message(mti, fields)
    
    @staticmethod
    def build_balance_inquiry(
        pan: str,
        stan: str,
        card_type: str = "Visa"
    ) -> bytes:
        """Build ISO 8583 0x0200 (Balance Inquiry)"""
        # MTI: 0200 (Balance Inquiry)
        mti = "0200"
        
        # Processing Code: 300000 (Balance Inquiry)
        processing_code = "300000"
        
        # Build field values
        fields = {
            2: pan,                    # PAN
            3: processing_code,        # Processing Code
            11: stan.zfill(6),        # STAN
            12: datetime.now().strftime("%H%M%S"),  # Time
            13: datetime.now().strftime("%m%d"),    # Date
            39: "00",                  # Response Code (placeholder)
            54: "0" * 16,              # Balance (placeholder)
        }
        
        return ISO8583Packager._build_message(mti, fields)
    
    @staticmethod
    def build_reversal_request(
        original_stan: str,
        amount: str
    ) -> bytes:
        """Build ISO 8583 0x0400 (Reversal Request)"""
        mti = "0400"
        processing_code = "000000"
        
        fields = {
            3: processing_code,
            4: amount.zfill(12),
            11: original_stan.zfill(6),
            12: datetime.now().strftime("%H%M%S"),
            13: datetime.now().strftime("%m%d"),
            39: "00",
        }
        
        return ISO8583Packager._build_message(mti, fields)
    
    @staticmethod
    def _build_message(mti: str, fields: Dict[int, str]) -> bytes:
        """Build complete ISO 8583 message"""
        # Build primary bitmap (16 hex digits = 64 bits)
        bitmap = 0
        for field_num in fields.keys():
            if 1 <= field_num <= 64:
                bitmap |= (1 << (64 - field_num))
        
        # Bitmap as 8 bytes (hex string)
        bitmap_str = f"{bitmap:016X}"
        message = mti + bitmap_str
        
        # Add field data
        for field_num in sorted(fields.keys()):
            if field_num == 1:
                continue
            value = fields[field_num]
            message += value
        
        # Convert to bytes
        msg_bytes = bytes.fromhex(message)
        
        # Prepend message length (2 bytes, big-endian)
        length = len(msg_bytes)
        return struct.pack('>H', length) + msg_bytes
    
    @staticmethod
    def parse_response(data: bytes) -> Dict:
        """Parse ISO 8583 response message"""
        if len(data) < 4:
            return {"error": "Message too short"}
        
        # Extract length
        length = struct.unpack('>H', data[0:2])[0]
        if len(data) < length + 2:
            return {"error": "Incomplete message"}
        
        msg_data = data[2:length+2]
        msg_hex = msg_data.hex().upper()
        
        # Extract MTI
        mti = msg_hex[0:4]
        
        # Extract bitmap
        bitmap_hex = msg_hex[4:20]
        bitmap = int(bitmap_hex, 16)
        
        # Extract fields based on bitmap
        response = {
            "mti": mti,
            "bitmap": bitmap_hex,
            "fields": {}
        }
        
        # Parse known fields
        pos = 20
        for field_num in range(2, 65):
            if bitmap & (1 << (64 - field_num)):
                # Field is present
                if field_num == 2:
                    # PAN (19 digits)
                    value = msg_hex[pos:pos+19]
                    response["fields"][field_num] = value
                    pos += 19
                elif field_num == 3:
                    # Processing Code (6 digits)
                    value = msg_hex[pos:pos+6]
                    response["fields"][field_num] = value
                    pos += 6
                elif field_num == 4:
                    # Amount (12 digits)
                    value = msg_hex[pos:pos+12]
                    response["fields"][field_num] = value
                    pos += 12
                elif field_num == 11:
                    # STAN (6 digits)
                    value = msg_hex[pos:pos+6]
                    response["fields"][field_num] = value
                    pos += 6
                elif field_num == 12:
                    # Time (6 digits)
                    value = msg_hex[pos:pos+6]
                    response["fields"][field_num] = value
                    pos += 6
                elif field_num == 13:
                    # Date (4 digits)
                    value = msg_hex[pos:pos+4]
                    response["fields"][field_num] = value
                    pos += 4
                elif field_num == 39:
                    # Response Code (2 digits)
                    value = msg_hex[pos:pos+2]
                    response["fields"][field_num] = value
                    pos += 2
                elif field_num == 38:
                    # Authorization Code (6 characters)
                    value = msg_hex[pos:pos+6]
                    response["fields"][field_num] = value
                    pos += 6
                elif field_num == 54:
                    # Balance (16 digits)
                    value = msg_hex[pos:pos+16]
                    response["fields"][field_num] = value
                    pos += 16
        
        return response


class JposGatewayClient:
    """Client for jPOS-EE ISO 8583 Gateway"""
    
    def __init__(self, host: str = "localhost", port: int = 8583):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self) -> bool:
        """Connect to jPOS gateway"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"✓ Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def send_message(self, message: bytes) -> Dict:
        """Send ISO 8583 message and receive response"""
        try:
            self.socket.sendall(message)
            response = self.socket.recv(4096)
            return ISO8583Packager.parse_response(response)
        except Exception as e:
            return {"error": str(e)}
    
    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
            print("✓ Connection closed")


def test_visa_transactions():
    """Test Visa card transactions"""
    print("\n" + "="*70)
    print("VISA CARD TRANSACTION TESTS")
    print("="*70)
    
    client = JposGatewayClient()
    if not client.connect():
        return
    
    # Test 1: Visa Authorization Request
    print("\n[Test 1] Visa Authorization Request - $100.00")
    visa_pan = "4111111111111111"  # Test Visa PAN
    msg = ISO8583Packager.build_authorization_request(
        pan=visa_pan,
        amount="10000",  # $100.00
        stan="000001",
        card_type="Visa"
    )
    response = client.send_message(msg)
    print_response(response, "Authorization Response")
    
    # Test 2: Visa Balance Inquiry
    print("\n[Test 2] Visa Balance Inquiry")
    msg = ISO8583Packager.build_balance_inquiry(
        pan=visa_pan,
        stan="000002",
        card_type="Visa"
    )
    response = client.send_message(msg)
    print_response(response, "Balance Inquiry Response")
    
    # Test 3: Visa Reversal
    print("\n[Test 3] Visa Reversal Request")
    msg = ISO8583Packager.build_reversal_request(
        original_stan="000001",
        amount="10000"
    )
    response = client.send_message(msg)
    print_response(response, "Reversal Response")
    
    client.close()


def test_mastercard_transactions():
    """Test MasterCard transactions"""
    print("\n" + "="*70)
    print("MASTERCARD TRANSACTION TESTS")
    print("="*70)
    
    client = JposGatewayClient()
    if not client.connect():
        return
    
    # Test 1: MC Authorization Request
    print("\n[Test 1] MasterCard Authorization Request - $250.00")
    mc_pan = "5555555555554444"  # Test MC PAN
    msg = ISO8583Packager.build_authorization_request(
        pan=mc_pan,
        amount="25000",  # $250.00
        stan="000010",
        card_type="MasterCard"
    )
    response = client.send_message(msg)
    print_response(response, "Authorization Response")
    
    # Test 2: MC Balance Inquiry
    print("\n[Test 2] MasterCard Balance Inquiry")
    msg = ISO8583Packager.build_balance_inquiry(
        pan=mc_pan,
        stan="000011",
        card_type="MasterCard"
    )
    response = client.send_message(msg)
    print_response(response, "Balance Inquiry Response")
    
    # Test 3: MC Reversal
    print("\n[Test 3] MasterCard Reversal Request")
    msg = ISO8583Packager.build_reversal_request(
        original_stan="000010",
        amount="25000"
    )
    response = client.send_message(msg)
    print_response(response, "Reversal Response")
    
    client.close()


def print_response(response: Dict, title: str):
    """Pretty print response"""
    print(f"\n{title}:")
    if "error" in response:
        print(f"  ✗ Error: {response['error']}")
    else:
        print(f"  MTI: {response.get('mti', 'N/A')}")
        fields = response.get("fields", {})
        
        # Map field numbers to names
        field_names = {
            2: "PAN",
            3: "Processing Code",
            4: "Amount",
            11: "STAN",
            12: "Time",
            13: "Date",
            39: "Response Code",
            38: "Auth Code",
            54: "Balance",
        }
        
        for field_num in sorted(fields.keys()):
            name = field_names.get(field_num, f"Field {field_num}")
            value = fields[field_num]
            
            # Format value based on field type
            if field_num == 4:
                # Amount
                amount_int = int(value)
                amount_str = f"${amount_int/100:.2f}"
                print(f"  {name}: {amount_str} (raw: {value})")
            elif field_num == 39:
                # Response Code
                code_map = {"00": "Approved", "30": "Format Error"}
                code_text = code_map.get(value, "Unknown")
                print(f"  {name}: {value} ({code_text})")
            elif field_num == 54:
                # Balance
                balance_int = int(value)
                balance_str = f"${balance_int/100:.2f}"
                print(f"  {name}: {balance_str} (raw: {value})")
            else:
                print(f"  {name}: {value}")


def main():
    """Run all tests"""
    print("\n" + "█"*70)
    print("ISO 8583 jPOS-EE Gateway Test Suite")
    print("Testing Visa and MasterCard Card Transactions")
    print("█"*70)
    
    # Check gateway connectivity
    client = JposGatewayClient()
    if not client.connect():
        print("\n✗ Cannot connect to jPOS Gateway on localhost:8583")
        print("   Make sure to start it with: cd jpos-ee && java -jar target/jpos-ee-1.0.0.jar")
        sys.exit(1)
    client.close()
    
    # Run test suites
    test_visa_transactions()
    test_mastercard_transactions()
    
    print("\n" + "█"*70)
    print("Test Suite Complete")
    print("█"*70 + "\n")


if __name__ == "__main__":
    main()
