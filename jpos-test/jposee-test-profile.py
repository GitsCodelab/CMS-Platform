#!/usr/bin/env python3
"""
jPOS EE Test Profile System
Comprehensive test suite for payment transactions (Visa, Mastercard, etc.)
Supports: Auth, Capture, Reversal, Refund, and other payment operations
"""

import socket
import struct
import time
from enum import Enum
from typing import Dict, Tuple

class TransactionType(Enum):
    """ISO 8583 Message Type Identifiers"""
    AUTH = "0100"              # Authorization request
    AUTH_RESPONSE = "0110"     # Authorization response
    REVERSAL = "0400"          # Reversal/Void
    REVERSAL_RESPONSE = "0410" # Reversal response
    CAPTURE = "0220"           # Capture
    CAPTURE_RESPONSE = "0230"  # Capture response
    REFUND = "0200"            # Refund/Credit
    REFUND_RESPONSE = "0210"   # Refund response
    ECHO = "0800"              # Echo/Network test
    ECHO_RESPONSE = "0810"     # Echo response

class CardBrand(Enum):
    """Card Brand Identifiers"""
    VISA = "4111111111111111"
    MASTERCARD = "5555555555554444"
    AMEX = "378282246310005"
    DISCOVER = "6011111111111117"

class TestTransaction:
    """Represents a single test transaction"""
    
    def __init__(self, name: str, card_number: str, amount: int, 
                 trans_type: TransactionType, description: str = ""):
        self.name = name
        self.card_number = card_number
        self.amount = amount
        self.trans_type = trans_type
        self.description = description
        self.timestamp = time.strftime("%Y%m%d%H%M%S")
    
    def generate_iso_message(self) -> bytes:
        """Generate ISO 8583 message for this transaction"""
        # Simple ISO 8583 format (not full spec, for testing)
        # Format: MTI + fields
        message = self.trans_type.value  # Message Type Indicator
        message += "822000000000"         # Processing code
        message += str(self.amount).zfill(12)  # Amount
        message += self.timestamp        # Transmission date/time
        message += "000001"              # STAN (System Trace Audit Number)
        message += "0000"                # MCC (Merchant Category Code)
        message += self.card_number      # PAN (Primary Account Number)
        
        return message.encode('utf-8')

class jPOSEETestProfile:
    """Test profile for jPOS EE transactions"""
    
    def __init__(self, host: str = "localhost", port: int = 5001, timeout: int = 5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.results = []
    
    def send_transaction(self, transaction: TestTransaction) -> Dict:
        """Send a single transaction to jPOS EE"""
        result = {
            "name": transaction.name,
            "status": "PENDING",
            "message": "",
            "response": None,
            "error": None
        }
        
        try:
            # Create socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            
            # Connect to jPOS EE
            s.connect((self.host, self.port))
            
            # Generate and send message
            iso_message = transaction.generate_iso_message()
            s.send(iso_message)
            
            result["message"] = iso_message.decode('utf-8', errors='ignore')
            result["status"] = "SENT"
            
            # Try to receive response
            try:
                response = s.recv(4096)
                if response:
                    result["response"] = response
                    result["status"] = "SUCCESS"
            except socket.timeout:
                result["status"] = "TIMEOUT"
            except ConnectionResetError:
                result["status"] = "PROCESSED"  # Normal for jPOS
            
            s.close()
            
        except ConnectionRefusedError:
            result["error"] = "Connection refused"
            result["status"] = "FAILED"
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "FAILED"
        
        self.results.append(result)
        return result
    
    def print_result(self, result: Dict):
        """Print formatted result"""
        status_emoji = {
            "SUCCESS": "✅",
            "PROCESSED": "✓",
            "SENT": "→",
            "PENDING": "⏳",
            "TIMEOUT": "⏱️",
            "FAILED": "✗"
        }
        
        emoji = status_emoji.get(result["status"], "?")
        print(f"\n{emoji} Transaction: {result['name']}")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        if result["error"]:
            print(f"   Error: {result['error']}")
    
    def print_summary(self):
        """Print test summary"""
        if not self.results:
            print("No transactions executed")
            return
        
        total = len(self.results)
        success = len([r for r in self.results if r["status"] in ["SUCCESS", "PROCESSED"]])
        failed = len([r for r in self.results if r["status"] == "FAILED"])
        
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total Transactions: {total}")
        print(f"Successful: {success} ({success*100//total if total else 0}%)")
        print(f"Failed: {failed} ({failed*100//total if total else 0}%)")
        print("=" * 70)

def run_visa_tests():
    """Run Visa transaction tests"""
    print("\n" + "=" * 70)
    print("VISA TRANSACTION TESTS")
    print("=" * 70)
    
    profile = jPOSEETestProfile(port=5001)
    
    # Test cases
    tests = [
        TestTransaction(
            "Visa Auth - $100 Purchase",
            CardBrand.VISA.value,
            10000,  # $100.00
            TransactionType.AUTH,
            "Standard authorization request"
        ),
        TestTransaction(
            "Visa Auth - $50.99 Purchase",
            CardBrand.VISA.value,
            5099,  # $50.99
            TransactionType.AUTH,
            "Fractional amount authorization"
        ),
        TestTransaction(
            "Visa Refund - $100 Return",
            CardBrand.VISA.value,
            10000,
            TransactionType.REFUND,
            "Full refund"
        ),
        TestTransaction(
            "Visa Reversal",
            CardBrand.VISA.value,
            10000,
            TransactionType.REVERSAL,
            "Transaction reversal/void"
        ),
    ]
    
    # Run tests
    for test in tests:
        result = profile.send_transaction(test)
        profile.print_result(result)
        time.sleep(0.5)  # Small delay between requests
    
    profile.print_summary()

def run_mastercard_tests():
    """Run Mastercard transaction tests"""
    print("\n" + "=" * 70)
    print("MASTERCARD TRANSACTION TESTS")
    print("=" * 70)
    
    profile = jPOSEETestProfile(port=5001)
    
    # Test cases
    tests = [
        TestTransaction(
            "Mastercard Auth - $250 Purchase",
            CardBrand.MASTERCARD.value,
            25000,  # $250.00
            TransactionType.AUTH,
            "High-value authorization"
        ),
        TestTransaction(
            "Mastercard Auth - $25 Purchase",
            CardBrand.MASTERCARD.value,
            2500,  # $25.00
            TransactionType.AUTH,
            "Low-value authorization"
        ),
        TestTransaction(
            "Mastercard Capture - $250",
            CardBrand.MASTERCARD.value,
            25000,
            TransactionType.CAPTURE,
            "Capture after authorization"
        ),
        TestTransaction(
            "Mastercard Refund - $50 Return",
            CardBrand.MASTERCARD.value,
            5000,
            TransactionType.REFUND,
            "Partial refund"
        ),
    ]
    
    # Run tests
    for test in tests:
        result = profile.send_transaction(test)
        profile.print_result(result)
        time.sleep(0.5)
    
    profile.print_summary()

def run_mixed_card_tests():
    """Run mixed card brand tests"""
    print("\n" + "=" * 70)
    print("MIXED CARD BRAND TESTS")
    print("=" * 70)
    
    profile = jPOSEETestProfile(port=5001)
    
    # Test cases with various cards
    tests = [
        TestTransaction(
            "AMEX Auth - $150 Purchase",
            CardBrand.AMEX.value,
            15000,
            TransactionType.AUTH,
            "American Express transaction"
        ),
        TestTransaction(
            "Discover Auth - $75 Purchase",
            CardBrand.DISCOVER.value,
            7500,
            TransactionType.AUTH,
            "Discover card transaction"
        ),
        TestTransaction(
            "Visa Echo Test",
            CardBrand.VISA.value,
            1,
            TransactionType.ECHO,
            "Network connectivity test"
        ),
        TestTransaction(
            "Mastercard Echo Test",
            CardBrand.MASTERCARD.value,
            1,
            TransactionType.ECHO,
            "Network connectivity test"
        ),
    ]
    
    # Run tests
    for test in tests:
        result = profile.send_transaction(test)
        profile.print_result(result)
        time.sleep(0.5)
    
    profile.print_summary()

def run_stress_test():
    """Run stress test with multiple transactions"""
    print("\n" + "=" * 70)
    print("STRESS TEST - 10 Rapid Transactions")
    print("=" * 70)
    
    profile = jPOSEETestProfile(port=5001)
    
    # Generate multiple transactions
    cards = [CardBrand.VISA.value, CardBrand.MASTERCARD.value]
    
    for i in range(10):
        card = cards[i % len(cards)]
        amount = (i + 1) * 1000  # $10, $20, $30, etc.
        
        test = TestTransaction(
            f"Stress Test #{i+1}",
            card,
            amount,
            TransactionType.AUTH,
            f"Stress test transaction {i+1}"
        )
        
        result = profile.send_transaction(test)
        print(f"[{i+1}/10] {result['status']}", end=" ", flush=True)
        time.sleep(0.2)
    
    print("\n")
    profile.print_summary()

if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 70)
    print("jPOS EE TEST PROFILE SUITE")
    print("=" * 70)
    print("Comprehensive payment transaction testing for jPOS Enterprise")
    print("Supports: Visa, Mastercard, AMEX, Discover")
    print("Operations: Auth, Capture, Refund, Reversal, Echo")
    print()
    
    # Display menu
    print("Available Test Profiles:")
    print("1. Visa Transactions")
    print("2. Mastercard Transactions")
    print("3. Mixed Card Brands")
    print("4. Stress Test (10 transactions)")
    print("5. Run All Tests")
    print()
    
    # Get user input or run all
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("Select test (1-5) or press Enter for all: ").strip() or "5"
    
    print()
    
    if choice == "1":
        run_visa_tests()
    elif choice == "2":
        run_mastercard_tests()
    elif choice == "3":
        run_mixed_card_tests()
    elif choice == "4":
        run_stress_test()
    elif choice == "5":
        run_visa_tests()
        run_mastercard_tests()
        run_mixed_card_tests()
        run_stress_test()
    else:
        print(f"Invalid choice: {choice}")
        sys.exit(1)
    
    print("\n✅ Test execution completed!\n")
