#!/usr/bin/env python3
"""
Real ISO 8583 Message Testing for jPOS-EE Gateway
Tests multiple transaction types with proper message encoding/decoding
"""

import socket
import struct
import sys
from datetime import datetime
from typing import Dict, Optional

# ============================================================================
# ISO 8583 Configuration
# ============================================================================

TPDU = b"\x60\x00\x00\x00\x00"  # Transport Protocol Data Unit

FIELD_DEFINITION = {
    2: {"type": "LLVAR", "len": None},      # PAN
    3: {"type": "FIXED", "len": 6},         # Processing Code
    4: {"type": "FIXED", "len": 12},        # Amount
    7: {"type": "FIXED", "len": 10},        # MMDDHHMMSS
    11: {"type": "FIXED", "len": 6},        # STAN
    12: {"type": "FIXED", "len": 6},        # HH MM SS
    13: {"type": "FIXED", "len": 4},        # MM DD
    22: {"type": "FIXED", "len": 3},        # POS Entry Mode
    25: {"type": "FIXED", "len": 2},        # Function Code
    35: {"type": "LLVAR", "len": None},     # Track 2
    37: {"type": "FIXED", "len": 12},       # RRN
    38: {"type": "FIXED", "len": 6},        # Auth Code
    39: {"type": "FIXED", "len": 2},        # Response Code
    41: {"type": "FIXED", "len": 8},        # Terminal ID
    42: {"type": "FIXED", "len": 15},       # Merchant ID
    49: {"type": "FIXED", "len": 3},        # Currency Code (USD)
    52: {"type": "BINARY", "len": 8},       # PIN Block
    54: {"type": "LLVAR", "len": None},     # Balance
    55: {"type": "LLLVAR_BIN", "len": None} # EMV Data
}

# Test Cards
TEST_CARDS = {
    "VISA": {
        "pan": "4111111111111111",
        "expiry": "2512",
        "brand": "Visa"
    },
    "MASTERCARD": {
        "pan": "5555555555554444",
        "expiry": "2512",
        "brand": "MasterCard"
    }
}

# ============================================================================
# Field Encoding
# ============================================================================

def encode_field(field_num: int, value) -> bytes:
    """Encode ISO 8583 field with proper formatting"""
    spec = FIELD_DEFINITION.get(field_num)
    if not spec:
        raise ValueError(f"Unknown field {field_num}")

    if spec["type"] == "FIXED":
        if isinstance(value, bytes):
            if len(value) != spec["len"]:
                raise ValueError(f"Field {field_num} must be {spec['len']} bytes")
            return value
        value_str = str(value).zfill(spec["len"])
        if len(value_str) != spec["len"]:
            raise ValueError(f"Field {field_num} must be {spec['len']} chars, got {len(value_str)}")
        return value_str.encode()

    elif spec["type"] == "LLVAR":
        if isinstance(value, bytes):
            length = len(value)
            return str(length).zfill(2).encode() + value
        length = len(value)
        return str(length).zfill(2).encode() + value.encode()

    elif spec["type"] == "BINARY":
        if isinstance(value, str):
            value = bytes.fromhex(value)
        if len(value) != spec["len"]:
            raise ValueError(f"Field {field_num} must be {spec['len']} bytes")
        return value

    elif spec["type"] == "LLLVAR_BIN":
        if isinstance(value, str):
            value = bytes.fromhex(value)
        length = len(value)
        return str(length).zfill(3).encode() + value

    raise ValueError(f"Unknown field type: {spec['type']}")


def generate_pin_block() -> bytes:
    """Generate a dummy PIN block (8 bytes)"""
    return bytes.fromhex("1234FFFFFFFFFFFF")


# ============================================================================
# ISO 8583 Message Builder
# ============================================================================

class ISO8583Builder:
    """Build ISO 8583 messages"""

    @staticmethod
    def build_0100(pan: str, amount: str, stan: str) -> bytes:
        """Build Authorization Request (0100)"""
        now = datetime.now()
        fields = {
            2: pan,
            3: "000000",  # ATM Withdrawal
            4: amount.zfill(12),
            7: now.strftime("%m%d%H%M%S"),
            11: stan.zfill(6),
            12: now.strftime("%H%M%S"),
            13: now.strftime("%m%d"),
            22: "021",  # Chip/PIN
            25: "00",   # Purchase
            35: f"{pan}=25122010000000000000",
            41: "TERMID01",
            42: "MERCHANT0000010",
            49: "840",  # USD
            52: generate_pin_block(),
            55: "9F2608A1A2A3A4A5A6A7",
        }
        return ISO8583Builder._build("0100", fields)

    @staticmethod
    def build_0200(pan: str, amount: str, stan: str) -> bytes:
        """Build Balance Inquiry (0200)"""
        now = datetime.now()
        fields = {
            2: pan,
            3: "300000",  # Balance Inquiry
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
            52: generate_pin_block(),
            55: "9F2608A1A2A3A4A5A6A7",
        }
        return ISO8583Builder._build("0200", fields)

    @staticmethod
    def build_0400(pan: str, amount: str, stan: str, rrn: str) -> bytes:
        """Build Reversal Request (0400)"""
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
            37: rrn.zfill(12),
            41: "TERMID01",
            42: "MERCHANT0000010",
            49: "840",
            52: generate_pin_block(),
            55: "9F2608A1A2A3A4A5A6A7",
        }
        return ISO8583Builder._build("0400", fields)

    @staticmethod
    def build_0800(stan: str) -> bytes:
        """Build Echo Test (0800)"""
        now = datetime.now()
        fields = {
            7: now.strftime("%m%d%H%M%S"),
            11: stan.zfill(6),
            12: now.strftime("%H%M%S"),
            13: now.strftime("%m%d"),
        }
        return ISO8583Builder._build("0800", fields)

    @staticmethod
    def _build(mti: str, fields: Dict[int, any]) -> bytes:
        """Build complete ISO 8583 message"""
        # Build bitmap
        bitmap = 0
        for f in fields:
            bitmap |= (1 << (64 - f))

        bitmap_bytes = bitmap.to_bytes(8, "big")
        data = mti.encode() + bitmap_bytes

        # Encode fields
        for f in sorted(fields):
            data += encode_field(f, fields[f])

        full_msg = TPDU + data
        return struct.pack(">H", len(full_msg)) + full_msg


# ============================================================================
# ISO 8583 Message Parser
# ============================================================================

class ISO8583Parser:
    """Parse ISO 8583 responses"""

    @staticmethod
    def parse(data: bytes) -> Dict:
        """Parse ISO 8583 message from bytes"""
        try:
            if len(data) < 2:
                return {"error": "Message too short"}

            length = struct.unpack(">H", data[:2])[0]
            msg = data[2:2 + length]

            if len(msg) < 12:
                return {"error": "Invalid message structure"}

            tpdu = msg[:5]
            mti = msg[5:9].decode()
            bitmap = int.from_bytes(msg[9:17], "big")

            pos = 17
            fields = {}

            for f in range(2, 65):  # Primary bitmap only covers fields 1-64
                if f > 0 and bitmap & (1 << (64 - f)):
                    spec = FIELD_DEFINITION.get(f)
                    if not spec:
                        continue

                    try:
                        if spec["type"] == "FIXED":
                            l = spec["len"]
                            if pos + l > len(msg):
                                break
                            val = msg[pos:pos + l].decode()
                            pos += l
                            fields[f] = val

                        elif spec["type"] == "LLVAR":
                            if pos + 2 > len(msg):
                                break
                            l = int(msg[pos:pos + 2].decode())
                            pos += 2
                            if pos + l > len(msg):
                                break
                            val = msg[pos:pos + l].decode()
                            pos += l
                            fields[f] = val

                        elif spec["type"] == "BINARY":
                            l = spec["len"]
                            if pos + l > len(msg):
                                break
                            val = msg[pos:pos + l].hex().upper()
                            pos += l
                            fields[f] = val

                        elif spec["type"] == "LLLVAR_BIN":
                            if pos + 3 > len(msg):
                                break
                            l = int(msg[pos:pos + 3].decode())
                            pos += 3
                            if pos + l > len(msg):
                                break
                            val = msg[pos:pos + l].hex().upper()
                            pos += l
                            fields[f] = val

                    except Exception as e:
                        fields[f] = f"PARSE_ERROR: {str(e)}"
                        break

            return {
                "mti": mti,
                "tpdu": tpdu.hex().upper(),
                "fields": fields
            }

        except Exception as e:
            return {"error": str(e)}


# ============================================================================
# Gateway Client
# ============================================================================

class GatewayClient:
    """ISO 8583 Gateway Client"""

    def __init__(self, host: str = "localhost", port: int = 8583, timeout: int = 5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None

    def connect(self) -> bool:
        """Connect to gateway"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    def send_message(self, msg: bytes) -> Optional[Dict]:
        """Send message and get response"""
        try:
            self.sock.sendall(msg)
            response = self.sock.recv(4096)
            return ISO8583Parser.parse(response)
        except socket.timeout:
            return {"error": "Socket timeout"}
        except Exception as e:
            return {"error": str(e)}

    def close(self):
        """Close connection"""
        if self.sock:
            self.sock.close()


# ============================================================================
# Test Suite
# ============================================================================

class TestRunner:
    """Run comprehensive ISO 8583 tests"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def test_authorization_request(self, card: str, amount: str) -> bool:
        """Test 0100 - Authorization Request"""
        client = GatewayClient()
        if not client.connect():
            self.failed += 1
            return False

        card_info = TEST_CARDS[card]
        pan = card_info["pan"]
        
        msg = ISO8583Builder.build_0100(pan, amount, "100001")
        print(f"\n📤 {card} Authorization Request - ${amount}")
        print(f"   PAN: {pan} | Amount: ${amount}")

        response = client.send_message(msg)
        client.close()

        if "error" in response:
            print(f"   ✗ Error: {response['error']}")
            self.failed += 1
            return False

        mti = response.get("mti", "")
        fields = response.get("fields", {})
        resp_code = fields.get(39, "00")

        print(f"   Response MTI: {mti}")
        print(f"   Response Code: {resp_code}")

        # Expected: 0110 response with code 00
        if mti == "0110" and resp_code == "00":
            print(f"   ✓ PASS")
            self.passed += 1
            return True
        else:
            print(f"   ✗ FAIL - Expected MTI 0110 with code 00")
            self.failed += 1
            return False

    def test_balance_inquiry(self, card: str) -> bool:
        """Test 0200 - Balance Inquiry"""
        client = GatewayClient()
        if not client.connect():
            self.failed += 1
            return False

        card_info = TEST_CARDS[card]
        pan = card_info["pan"]
        
        msg = ISO8583Builder.build_0200(pan, "000000", "100002")
        print(f"\n📤 {card} Balance Inquiry")
        print(f"   PAN: {pan}")

        response = client.send_message(msg)
        client.close()

        if "error" in response:
            print(f"   ✗ Error: {response['error']}")
            self.failed += 1
            return False

        mti = response.get("mti", "")
        fields = response.get("fields", {})
        resp_code = fields.get(39, "00")

        print(f"   Response MTI: {mti}")
        print(f"   Response Code: {resp_code}")

        # Expected: 0210 response with code 00
        if mti == "0210" and resp_code == "00":
            print(f"   ✓ PASS")
            self.passed += 1
            return True
        else:
            print(f"   ✗ FAIL - Expected MTI 0210 with code 00")
            self.failed += 1
            return False

    def test_reversal(self, card: str, amount: str) -> bool:
        """Test 0400 - Reversal Request"""
        client = GatewayClient()
        if not client.connect():
            self.failed += 1
            return False

        card_info = TEST_CARDS[card]
        pan = card_info["pan"]
        
        msg = ISO8583Builder.build_0400(pan, amount, "100003", "123456789012")
        print(f"\n📤 {card} Reversal Request - ${amount}")
        print(f"   PAN: {pan} | Amount: ${amount}")

        response = client.send_message(msg)
        client.close()

        if "error" in response:
            print(f"   ✗ Error: {response['error']}")
            self.failed += 1
            return False

        mti = response.get("mti", "")
        fields = response.get("fields", {})
        resp_code = fields.get(39, "00")

        print(f"   Response MTI: {mti}")
        print(f"   Response Code: {resp_code}")

        # Expected: 0410 response with code 00
        if mti == "0410" and resp_code == "00":
            print(f"   ✓ PASS")
            self.passed += 1
            return True
        else:
            print(f"   ✗ FAIL - Expected MTI 0410 with code 00")
            self.failed += 1
            return False

    def test_echo(self) -> bool:
        """Test 0800 - Echo Test"""
        client = GatewayClient()
        if not client.connect():
            self.failed += 1
            return False

        msg = ISO8583Builder.build_0800("100004")
        print(f"\n📤 Echo Test")

        response = client.send_message(msg)
        client.close()

        if "error" in response:
            print(f"   ✗ Error: {response['error']}")
            self.failed += 1
            return False

        mti = response.get("mti", "")
        resp_code = response.get("fields", {}).get(39, "00")

        print(f"   Response MTI: {mti}")
        print(f"   Response Code: {resp_code}")

        # Expected: 0810 response with code 00
        if mti == "0810" and resp_code == "00":
            print(f"   ✓ PASS")
            self.passed += 1
            return True
        else:
            print(f"   ✗ FAIL - Expected MTI 0810 with code 00")
            self.failed += 1
            return False

    def run_all(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("ISO 8583 REAL MESSAGE TESTING - jPOS-EE Gateway")
        print("="*70)

        # VISA Tests
        print("\n" + "-"*70)
        print("VISA Card Tests")
        print("-"*70)
        self.test_authorization_request("VISA", "10000")
        self.test_balance_inquiry("VISA")
        self.test_reversal("VISA", "10000")

        # MasterCard Tests
        print("\n" + "-"*70)
        print("MasterCard Tests")
        print("-"*70)
        self.test_authorization_request("MASTERCARD", "25000")
        self.test_balance_inquiry("MASTERCARD")
        self.test_reversal("MASTERCARD", "25000")

        # Echo Test
        print("\n" + "-"*70)
        print("Gateway Tests")
        print("-"*70)
        self.test_echo()

        # Summary
        print("\n" + "="*70)
        print(f"RESULTS: {self.passed} PASSED, {self.failed} FAILED")
        print("="*70 + "\n")

        return self.failed == 0


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
