#!/usr/bin/env python3
"""
jPOS EE Test Profile System
Comprehensive test suite for payment transactions (Visa, Mastercard, etc.)
Supports: Auth, Capture, Reversal, Refund, and other payment operations
"""

import socket
import struct
import time
import requests
import json
from enum import Enum
from typing import Dict, Tuple
from datetime import datetime

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
        self.api_url = "http://localhost:8000/jposee"  # Backend API URL
        self.persisted_count = 0
        self.transaction_counter = 0  # Counter for unique transaction IDs
    
    def send_transaction(self, transaction: TestTransaction) -> Dict:
        """Send a single transaction to jPOS EE"""
        result = {
            "name": transaction.name,
            "status": "PENDING",
            "message": "",
            "response": None,
            "error": None,
            "api_persisted": False,
            "api_error": None,
            "transaction_id": None
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
                    
                    # NEW: Persist response to backend API
                    api_result = self._persist_to_api(transaction, response)
                    result["api_persisted"] = api_result.get("success", False)
                    result["transaction_id"] = api_result.get("transaction_id")
                    result["api_error"] = api_result.get("error") if not api_result.get("success") else None
                    
            except socket.timeout:
                result["status"] = "TIMEOUT"
            except ConnectionResetError:
                result["status"] = "PROCESSED"  # Normal for jPOS
                
                # NEW: Still try to persist even if connection reset
                api_result = self._persist_to_api(transaction, None)
                result["api_persisted"] = api_result.get("success", False)
                result["transaction_id"] = api_result.get("transaction_id")
                result["api_error"] = api_result.get("error") if not api_result.get("success") else None
            
            s.close()
            
        except ConnectionRefusedError:
            result["error"] = "Connection refused"
            result["status"] = "FAILED"
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "FAILED"
        
        self.results.append(result)
        return result
    
    def _persist_to_api(self, transaction: TestTransaction, response: bytes) -> Dict:
        """Persist transaction to backend API"""
        try:
            # Increment counter to ensure unique txn_id
            self.transaction_counter += 1
            
            # Build ISO-like payload from transaction
            iso_data = {
                "mti": transaction.trans_type.value,
                "txn_id": f"TEST-{transaction.timestamp}-{self.transaction_counter}",  # Unique ID
                "field_2": transaction.card_number,  # PAN
                "field_3": "000000",  # Processing code
                "field_4": str(transaction.amount),
                "field_7": transaction.timestamp,
                "field_11": "000001",  # STAN
                "field_18": "5411",  # MCC
                "merchant_id": "TEST_MERCHANT",
                "currency": "USD",
                "card_last4": transaction.card_number[-4:],
                "card_bin": transaction.card_number[:6]
            }
            
            # POST to webhook endpoint
            response_obj = requests.post(
                f"{self.api_url}/webhook/iso-message",
                json=iso_data,
                timeout=5
            )
            
            if response_obj.status_code == 201:
                data = response_obj.json()
                return {
                    "success": True,
                    "transaction_id": data.get("transaction_id"),
                    "txn_id": data.get("txn_id"),
                    "message": data.get("message")
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned {response_obj.status_code}"
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": f"Cannot connect to API at {self.api_url}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
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
        persist_emoji = "💾" if result.get("api_persisted") else "❌"
        
        print(f"\n{emoji} Transaction: {result['name']}")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        if result.get("transaction_id"):
            print(f"   Database ID: {result['transaction_id']}")
        persist_status = "✅ SAVED" if result.get("api_persisted") else "❌ NOT SAVED"
        if result.get("api_error"):
            persist_status += f" ({result['api_error']})"
        print(f"   {persist_emoji} API Persistence: {persist_status}")
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
        persisted = len([r for r in self.results if r.get("api_persisted")])
        
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total Transactions: {total}")
        print(f"Successful: {success} ({success*100//total if total else 0}%)")
        print(f"Failed: {failed} ({failed*100//total if total else 0}%)")
        print(f"💾 Persisted to Database: {persisted}/{total} ({persisted*100//total if total else 0}%)")
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
